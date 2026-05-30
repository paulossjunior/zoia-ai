from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.domain.command import Command
from app.domain.context import CommandContext
from app.domain.status import CommandStatus
from app.infrastructure.memory_command_repository import MemoryCommandRepository


class ExplodingQueue:
    def publish(self, command_id: str) -> None:
        self.command_id = command_id

    def consume(self, timeout: int = 0) -> str | None:
        return None


class GuardQueue:
    def publish(self, command_id: str) -> None:
        raise AssertionError("status lookup must not publish to queue")

    def consume(self, timeout: int = 0) -> str | None:
        raise AssertionError("status lookup must not consume from queue")


def test_post_commands_valid_request_returns_202_and_queued() -> None:
    repo = MemoryCommandRepository()
    queue = ExplodingQueue()
    client = TestClient(create_app(repo, queue))

    response = client.post("/commands", json={"type": "TEST_COMMAND", "payload": {"message": "hello"}})

    assert response.status_code == 202
    body = response.json()
    assert body["command_id"]
    assert body["status"] == "queued"
    command = repo.get_by_id(body["command_id"])
    assert command is not None
    assert command.payload == {"message": "hello"}
    assert command.request_received_at is not None
    assert command.status == CommandStatus.QUEUED
    assert command.callback_status.value == "not_required"


def test_post_commands_full_request_persists_external_id_and_callback() -> None:
    repo = MemoryCommandRepository()
    client = TestClient(create_app(repo, ExplodingQueue()))

    response = client.post(
        "/commands",
        json={
            "type": "TEST_COMMAND",
            "payload": {"message": "hello"},
            "external_id": "BOLSISTA-12345",
            "callback": "https://sistema-origem.com/api/callback",
        },
    )

    assert response.status_code == 202
    command = repo.get_by_id(response.json()["command_id"])
    assert command.external_id == "BOLSISTA-12345"
    assert command.callback == "https://sistema-origem.com/api/callback"
    assert command.callback_status.value == "pending"


def test_post_commands_blank_callback_is_not_required() -> None:
    repo = MemoryCommandRepository()
    client = TestClient(create_app(repo, ExplodingQueue()))

    response = client.post("/commands", json={"type": "TEST_COMMAND", "payload": {}, "callback": "   "})

    assert response.status_code == 202
    command = repo.get_by_id(response.json()["command_id"])
    assert command.callback is None
    assert command.callback_status.value == "not_required"


def test_post_commands_validation_errors_return_400() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), ExplodingQueue()))

    invalid_payloads = [
        {"payload": {"message": "hello"}},
        {"type": "", "payload": {"message": "hello"}},
        {"type": "TEST_COMMAND"},
        {"type": "TEST_COMMAND", "payload": "not-object"},
    ]

    for payload in invalid_payloads:
        assert client.post("/commands", json=payload).status_code == 400

    assert client.post("/commands", content="{", headers={"content-type": "application/json"}).status_code == 400


def test_api_submission_does_not_execute_handlers(monkeypatch) -> None:
    called = False

    def forbidden_handle(self, context: CommandContext) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("app.commands.test_command.handlers.BusinessCommandHandler.handle", forbidden_handle)
    client = TestClient(create_app(MemoryCommandRepository(), ExplodingQueue()))

    response = client.post("/commands", json={"type": "TEST_COMMAND", "payload": {"message": "hello"}})

    assert response.status_code == 202
    assert called is False


def test_get_commands_record_returns_200_for_known_command() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_completed({"echo": "hello"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["command_id"] == command.id
    assert "id" not in body
    assert body["type"] == "TEST_COMMAND"
    assert body["payload"] == {"message": "hello"}
    assert body["status"] == CommandStatus.COMPLETED.value
    assert body["response_payload"] == {"echo": "hello"}
    assert body["callback_status"] == "not_required"
    assert body["request_received_at"]
    assert body["processing_started_at"]
    assert body["processing_finished_at"]
    assert body["error_message"] is None


def test_get_commands_record_returns_queued_payload_and_receipt_timestamp() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["payload"] == {"message": "hello"}
    assert body["status"] == "queued"
    assert body["request_received_at"]
    assert body["processing_started_at"] is None
    assert body["processing_finished_at"] is None
    assert body["response_payload"] is None
    assert body["callback_status"] == "not_required"
    assert body["error_message"] is None


def test_get_commands_record_returns_failed_error_and_null_response() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_failed("boom")
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["payload"] == {"message": "hello"}
    assert body["response_payload"] is None
    assert body["error_message"] == "boom"
    assert body["processing_finished_at"]


def test_get_commands_status_does_not_publish_or_execute_handlers(monkeypatch) -> None:
    called = False

    def forbidden_handle(self, context: CommandContext) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("app.commands.test_command.handlers.BusinessCommandHandler.handle", forbidden_handle)
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    assert called is False


def test_get_commands_status_only_returns_id_and_status_for_known_command() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}/status")

    assert response.status_code == 200
    assert response.json() == {
        "command_id": command.id,
        "status": "processing",
        "callback_status": "not_required",
    }


def test_get_commands_status_only_omits_detail_fields() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_completed({"echo": "hello"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    body = client.get(f"/commands/{command.id}/status").json()

    assert set(body) == {"command_id", "status", "callback_status"}
    for field in ("payload", "response_payload", "error_message", "request_received_at"):
        assert field not in body


def test_get_commands_status_only_does_not_publish_or_execute_handlers(monkeypatch) -> None:
    called = False

    def forbidden_handle(self, context: CommandContext) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("app.commands.test_command.handlers.BusinessCommandHandler.handle", forbidden_handle)
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}/status")

    assert response.status_code == 200
    assert called is False


def test_get_commands_status_only_errors() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    assert client.get("/commands/not-a-uuid/status").status_code == 400
    assert client.get("/commands/00000000-0000-4000-8000-000000000001/status").status_code == 404


def test_get_commands_status_malformed_id_returns_400() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    response = client.get("/commands/not-a-uuid")

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid command_id"}


def test_get_commands_status_unknown_id_returns_404() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    response = client.get("/commands/00000000-0000-4000-8000-000000000001")

    assert response.status_code == 404
    assert response.json() == {"detail": "command not found"}


def test_get_commands_external_id_returns_latest_command() -> None:
    repo = MemoryCommandRepository()
    older = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"version": 1}, external_id="EXT-1")
    newer = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"version": 2}, external_id="EXT-1")
    older.request_received_at = newer.request_received_at - timedelta(seconds=10)
    repo.save(older)
    repo.save(newer)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get("/commands/external/EXT-1")

    assert response.status_code == 200
    assert response.json()["command_id"] == newer.id
    assert response.json()["external_id"] == "EXT-1"


def test_get_commands_external_id_unknown_returns_404() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    response = client.get("/commands/external/EXT-404")

    assert response.status_code == 404
    assert response.json() == {"detail": "command not found"}


def test_list_commands_filters_by_status_and_returns_summaries() -> None:
    repo = MemoryCommandRepository()
    failed = Command(id=str(uuid4()), type="SEND_EMAIL", payload={"message": "failed"})
    failed.mark_processing()
    failed.mark_failed("boom")
    completed = Command(id=str(uuid4()), type="GENERATE_REPORT", payload={"message": "done"})
    completed.mark_processing()
    completed.mark_completed({"ok": True})
    repo.save(failed)
    repo.save(completed)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get("/commands?status=failed&page=1&page_size=20")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"] == [{"id": failed.id, "type": "SEND_EMAIL", "status": "failed"}]
    assert "payload" not in body["items"][0]


def test_list_commands_invalid_status_and_pagination_return_400() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    assert client.get("/commands?status=unknown").json() == {"detail": "invalid status"}
    assert client.get("/commands?status=unknown").status_code == 400
    assert client.get("/commands?page=0&page_size=20").json() == {"detail": "invalid pagination"}
    assert client.get("/commands?page=0&page_size=20").status_code == 400


def test_list_commands_does_not_publish_or_execute_handlers(monkeypatch) -> None:
    called = False

    def forbidden_handle(self, context: CommandContext) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("app.commands.test_command.handlers.BusinessCommandHandler.handle", forbidden_handle)
    repo = MemoryCommandRepository()
    repo.save(Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"}))
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get("/commands")

    assert response.status_code == 200
    assert called is False


def test_get_commands_status_error_bodies_do_not_expose_internals() -> None:
    client = TestClient(create_app(MemoryCommandRepository(), GuardQueue()))

    responses = [
        client.get("/commands/not-a-uuid"),
        client.get("/commands/00000000-0000-4000-8000-000000000001"),
    ]

    for response in responses:
        body = str(response.json()).lower()
        for term in ("repository", "redis", "storage", "queue"):
            assert term not in body
