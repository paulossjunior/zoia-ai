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
    return GetCommandStatus(repository).execute(GetCommandStatusRequest(command_id=command.id))


def test_get_command_status_returns_only_id_and_status_for_all_states() -> None:
    for state, expected in [
        ("queued", CommandStatus.QUEUED),
        ("processing", CommandStatus.PROCESSING),
        ("completed", CommandStatus.COMPLETED),
        ("failed", CommandStatus.FAILED),
    ]:
        command = make_command(str(uuid4()), state)

        result = _execute(command)

        assert result.command_id == command.id
        assert result.status == expected
        assert result.callback_status.value == "not_required"
        assert set(result.__dataclass_fields__) == {"command_id", "status", "callback_status"}


def test_get_command_status_rejects_malformed_id_before_repository_lookup() -> None:
    use_case = GetCommandStatus(FailingRepository())  # type: ignore[arg-type]

    with pytest.raises(InvalidCommandIdError, match="invalid command_id"):
        use_case.execute(GetCommandStatusRequest(command_id="not-a-uuid"))


def test_get_command_status_unknown_id_raises_not_found() -> None:
    use_case = GetCommandStatus(MemoryCommandRepository())

    with pytest.raises(CommandStatusNotFoundError, match="command not found"):
        use_case.execute(GetCommandStatusRequest(command_id=UNKNOWN_COMMAND_ID))
