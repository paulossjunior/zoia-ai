from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.get_command_status import (
    CommandStatusNotFoundError,
    GetCommandStatus,
    GetCommandStatusRequest,
    InvalidCommandIdError,
)
from app.domain.command import Command
from app.domain.status import CommandStatus
from app.infrastructure.memory_command_repository import MemoryCommandRepository


KNOWN_COMMAND_ID = "00000000-0000-4000-8000-000000000000"
UNKNOWN_COMMAND_ID = "00000000-0000-4000-8000-000000000001"
SUCCESS_STATUS_EXAMPLE = {
    "command_id": KNOWN_COMMAND_ID,
    "type": "TEST_COMMAND",
    "status": "completed",
    "error_message": None,
}
INVALID_ID_ERROR = {"detail": "invalid command_id"}
NOT_FOUND_ERROR = {"detail": "command not found"}


class FailingRepository:
    def save(self, command: Command) -> None:
        raise AssertionError("save must not be called")

    def get_by_id(self, command_id: str) -> Command | None:
        raise AssertionError("get_by_id must not be called for malformed ids")

    def update(self, command: Command) -> None:
        raise AssertionError("update must not be called")


def _repository_with(command: Command) -> MemoryCommandRepository:
    repository = MemoryCommandRepository()
    repository.save(command)
    return repository


def _execute(command: Command):
    return GetCommandStatus(_repository_with(command)).execute(GetCommandStatusRequest(command_id=command.id))


def test_get_command_status_returns_queued_view() -> None:
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})

    result = _execute(command)

    assert result.command_id == command.id
    assert result.type == "TEST_COMMAND"
    assert result.status == CommandStatus.QUEUED
    assert result.created_at == command.created_at
    assert result.started_at is None
    assert result.completed_at is None
    assert result.error_message is None


def test_get_command_status_returns_processing_view() -> None:
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()

    result = _execute(command)

    assert result.status == CommandStatus.PROCESSING
    assert result.started_at == command.started_at
    assert result.completed_at is None
    assert result.error_message is None


def test_get_command_status_returns_completed_view() -> None:
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_completed()

    result = _execute(command)

    assert result.status == CommandStatus.COMPLETED
    assert result.completed_at == command.completed_at
    assert result.error_message is None


def test_get_command_status_returns_failed_view() -> None:
    command = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"message": "hello"})
    command.mark_processing()
    command.mark_failed("boom")

    result = _execute(command)

    assert result.status == CommandStatus.FAILED
    assert result.completed_at == command.completed_at
    assert result.error_message == "boom"


def test_get_command_status_rejects_malformed_id_before_repository_lookup() -> None:
    use_case = GetCommandStatus(FailingRepository())  # type: ignore[arg-type]

    with pytest.raises(InvalidCommandIdError, match="invalid command_id"):
        use_case.execute(GetCommandStatusRequest(command_id="not-a-uuid"))


def test_get_command_status_unknown_id_raises_not_found() -> None:
    use_case = GetCommandStatus(MemoryCommandRepository())

    with pytest.raises(CommandStatusNotFoundError, match="command not found"):
        use_case.execute(GetCommandStatusRequest(command_id=UNKNOWN_COMMAND_ID))
