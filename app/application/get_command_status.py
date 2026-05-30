"""Read-only use case for querying command lifecycle status only."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.get_command import InvalidCommandIdError, _validate_command_id
from app.domain.ports import CommandRepository
from app.domain.status import CallbackStatus, CommandStatus


class CommandStatusNotFoundError(Exception):
    """Raised when no command exists for a valid status lookup id."""

    pass


@dataclass(frozen=True)
class GetCommandStatusRequest:
    """Input contract for reading command status by id."""

    command_id: str


@dataclass(frozen=True)
class GetCommandStatusResult:
    """Lightweight command status view returned to external clients."""

    command_id: str
    status: CommandStatus
    callback_status: CallbackStatus

    @property
    def id(self) -> str:
        """Backward-compatible alias for previous application tests."""
        return self.command_id


class GetCommandStatus:
    """Fetch command status without mutating state or triggering processing."""

    def __init__(self, repository: CommandRepository) -> None:
        """Create the use case with the command repository port."""
        self.repository = repository

    def execute(self, request: GetCommandStatusRequest) -> GetCommandStatusResult:
        """Validate the id, load the command, and map it to a status-only view."""
        command_id = _validate_command_id(request.command_id)
        command = self.repository.get_by_id(command_id)
        if command is None:
            raise CommandStatusNotFoundError("command not found")

        return GetCommandStatusResult(
            command_id=command.id,
            status=command.status,
            callback_status=command.callback_status,
        )
