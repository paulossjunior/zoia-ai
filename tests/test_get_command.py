from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.get_command import CommandNotFoundError, GetCommand, GetCommandRequest, InvalidCommandIdError
from app.domain.command import Command
from app.domain.status import CommandStatus
from app.infrastructure.memory_command_repository import MemoryCommandRepository
from tests.conftest import make_command


UNKNOWN_COMMAND_ID = "00000000-0000-4000-8000-000000000001"


class FailingRepository:
    def save(self, command: Command) -> None:
        raise AssertionError("save must not be called")

    def get_by_id(self, command_id: str) -> Command | None:
        raise AssertionError("get_by_id must not be called for malformed ids")

    def update(self, command: Command) -> None:
        raise AssertionError("update must not be called")

    def list(self, status=None, page: int = 1, page_size: int = 20):
        raise AssertionError("list must not be called")


def _execute(command: Command):
    repository = MemoryCommandRepository()
    repository.save(command)
    return GetCommand(repository).execute(GetCommandRequest(command_id=command.id))


def test_get_command_returns_queued_record() -> None:
    command = make_command(str(uuid4()), "queued")

    result = _execute(command)

    assert result.id == command.id
    assert result.type == "TEST_COMMAND"
    assert result.status == CommandStatus.QUEUED
    assert result.payload == command.payload
    assert result.response is None
    assert result.error_message is None
    assert result.request_received_at == command.request_received_at
    assert result.processing_started_at is None
    assert result.processing_finished_at is None


def test_get_command_returns_completed_record() -> None:
    command = make_command(str(uuid4()), "completed")

    result = _execute(command)

    assert result.status == CommandStatus.COMPLETED
    assert result.response == {"echo": command.id}
    assert result.error_message is None
    assert result.processing_started_at is not None
    assert result.processing_finished_at is not None


def test_get_command_returns_failed_record() -> None:
    command = make_command(str(uuid4()), "failed")

    result = _execute(command)

    assert result.status == CommandStatus.FAILED
    assert result.response is None
    assert result.error_message == f"{command.id} failed"


def test_get_command_returns_processing_record() -> None:
    command = make_command(str(uuid4()), "processing")

    result = _execute(command)

    assert result.status == CommandStatus.PROCESSING
    assert result.processing_started_at is not None
    assert result.processing_finished_at is None


def test_get_command_rejects_malformed_id_before_repository_lookup() -> None:
    use_case = GetCommand(FailingRepository())  # type: ignore[arg-type]

    with pytest.raises(InvalidCommandIdError, match="invalid command_id"):
        use_case.execute(GetCommandRequest(command_id="not-a-uuid"))


def test_get_command_unknown_id_raises_not_found() -> None:
    use_case = GetCommand(MemoryCommandRepository())

    with pytest.raises(CommandNotFoundError, match="command not found"):
        use_case.execute(GetCommandRequest(command_id=UNKNOWN_COMMAND_ID))
