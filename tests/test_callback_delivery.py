from __future__ import annotations

import pytest

from app.application.handler_registry import HandlerRegistry
from app.application.pipelines import SequentialCommandPipeline
from app.application.process_command import ProcessCommand, ProcessCommandRequest, build_callback_payload
from app.domain.command import Command
from app.domain.status import CallbackStatus, CommandStatus
from app.infrastructure.http_callback_client import HttpCallbackClient
from tests.conftest import FakeHandler


class RecordingCallbackClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, dict]] = []

    def send(self, url: str, payload: dict) -> None:
        self.calls.append((url, payload))
        if self.fail:
            raise RuntimeError("callback unavailable")


class FakeHttpResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class FakeHttpClient:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.calls: list[tuple[str, dict, float]] = []

    def post(self, url: str, json: dict, timeout: float) -> FakeHttpResponse:
        self.calls.append((url, json, timeout))
        return FakeHttpResponse(self.status_code)


def _registry(handler: FakeHandler) -> HandlerRegistry:
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", SequentialCommandPipeline([handler]))
    return registry


def test_callback_payload_contract_for_success_and_failure() -> None:
    completed = Command(id="cmd-1", type="TEST_COMMAND", payload={}, external_id="EXT-1", callback="https://callback")
    completed.mark_processing()
    completed.mark_completed({"ok": True})
    failed = Command(id="cmd-2", type="TEST_COMMAND", payload={}, external_id="EXT-1", callback="https://callback")
    failed.mark_processing()
    failed.mark_failed("boom")

    assert build_callback_payload(completed) == {"external_id": "EXT-1", "status": "completed", "payload": {"ok": True}}
    assert build_callback_payload(failed) == {"external_id": "EXT-1", "status": "failed", "payload": {"message": "boom"}}


def test_completed_command_with_callback_sends_and_marks_sent(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={}, external_id="EXT-1", callback="https://callback")
    repository.save(command)
    client = RecordingCallbackClient()

    result = ProcessCommand(repository, _registry(FakeHandler("ok")), client).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.COMPLETED
    assert client.calls == [("https://callback", {"external_id": "EXT-1", "status": "completed", "payload": {"handler": "ok"}})]
    assert saved.callback_status == CallbackStatus.SENT
    assert saved.callback_sent_at is not None
    assert saved.retry_count == 1


def test_failed_command_with_callback_sends_failure_payload(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={}, external_id="EXT-1", callback="https://callback")
    repository.save(command)
    client = RecordingCallbackClient()

    result = ProcessCommand(repository, _registry(FakeHandler("bad", fail=True)), client).execute(ProcessCommandRequest(command_id="cmd-1"))

    assert result.status == CommandStatus.FAILED
    assert client.calls == [("https://callback", {"external_id": "EXT-1", "status": "failed", "payload": {"message": "bad failed"}})]


def test_command_without_callback_does_not_call_client(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={})
    repository.save(command)
    client = RecordingCallbackClient()

    ProcessCommand(repository, _registry(FakeHandler("ok")), client).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert client.calls == []
    assert saved.callback_status == CallbackStatus.NOT_REQUIRED


def test_callback_failure_preserves_processing_status_and_response(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={}, callback="https://callback")
    repository.save(command)

    result = ProcessCommand(repository, _registry(FakeHandler("ok")), RecordingCallbackClient(fail=True)).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.COMPLETED
    assert saved.status == CommandStatus.COMPLETED
    assert saved.response_payload == {"handler": "ok"}
    assert saved.callback_status == CallbackStatus.FAILED
    assert saved.callback_error_message == "callback unavailable"
    assert saved.retry_count == 1


def test_http_callback_client_raises_for_non_2xx_response() -> None:
    client = FakeHttpClient(500)

    with pytest.raises(RuntimeError, match="HTTP 500"):
        HttpCallbackClient(client=client).send("https://callback", {"status": "completed"})


def test_http_callback_client_accepts_2xx_response() -> None:
    client = FakeHttpClient(204)

    HttpCallbackClient(client=client).send("https://callback", {"status": "completed"})

    assert client.calls == [("https://callback", {"status": "completed"}, 5.0)]
