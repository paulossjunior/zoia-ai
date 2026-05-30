from __future__ import annotations

import pytest

from app.application.submit_command import InvalidCommandError, SubmitCommand, SubmitCommandRequest
from app.domain.status import CommandStatus


class RecordingRepository:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.commands = {}

    def save(self, command) -> None:
        self.events.append("save")
        self.commands[command.id] = command

    def get_by_id(self, command_id: str):
        return self.commands.get(command_id)

    def update(self, command) -> None:
        self.commands[command.id] = command


class RecordingQueue:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.published: list[str] = []

    def publish(self, command_id: str) -> None:
        self.events.append("publish")
        self.published.append(command_id)

    def consume(self, timeout: int = 0) -> str | None:
        return None


def test_submit_command_creates_persists_then_queues(repository, queue, sample_payload) -> None:
    use_case = SubmitCommand(repository, queue)

    result = use_case.execute(SubmitCommandRequest(type="TEST_COMMAND", payload=sample_payload))

    command = repository.get_by_id(result.command_id)
    assert command is not None
    assert command.status == CommandStatus.QUEUED
    assert command.payload == sample_payload
    assert command.response is None
    assert command.error_message is None
    assert command.request_received_at is not None
    assert command.processing_started_at is None
    assert command.processing_finished_at is None
    assert queue.published == [result.command_id]


def test_submit_command_persists_before_queue_publication(sample_payload) -> None:
    events: list[str] = []
    repository = RecordingRepository(events)
    queue = RecordingQueue(events)

    result = SubmitCommand(repository, queue).execute(SubmitCommandRequest(type="TEST_COMMAND", payload=sample_payload))

    assert events == ["save", "publish"]
    assert repository.get_by_id(result.command_id) is not None
    assert queue.published == [result.command_id]


def test_submit_command_invalid_envelope_does_not_persist_or_enqueue(repository, queue) -> None:
    use_case = SubmitCommand(repository, queue)

    with pytest.raises(InvalidCommandError):
        use_case.execute(SubmitCommandRequest(type="", payload={}))

    with pytest.raises(InvalidCommandError):
        use_case.execute(SubmitCommandRequest(type="TEST_COMMAND", payload="bad"))  # type: ignore[arg-type]

    assert queue.published == []
