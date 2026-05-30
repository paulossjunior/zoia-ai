from __future__ import annotations

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
    assert repo.get_by_id(body["command_id"]) is not None


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


def test_get_commands_status_returns_200_for_known_command() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_completed()
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["command_id"] == command.id
    assert body["type"] == "TEST_COMMAND"
    assert body["status"] == CommandStatus.COMPLETED.value
    assert body["created_at"]
    assert body["started_at"]
    assert body["completed_at"]
    assert body["error_message"] is None


def test_get_commands_status_does_not_include_payload() -> None:
    repo = MemoryCommandRepository()
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "secret"})
    repo.save(command)
    client = TestClient(create_app(repo, GuardQueue()))

    response = client.get(f"/commands/{command.id}")

    assert response.status_code == 200
    assert "payload" not in response.json()


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
