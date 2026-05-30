"""Read-only use case for querying command lifecycle status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.ports import CommandRepository
from app.domain.status import CommandStatus


class InvalidCommandIdError(ValueError):
    """Raised when a status lookup receives a malformed command id."""

    pass


class CommandStatusNotFoundError(Exception):
    """Raised when no command exists for a valid status lookup id."""

    pass


@dataclass(frozen=True)
class GetCommandStatusRequest:
    """Input contract for reading command status by id."""

    command_id: str


@dataclass(frozen=True)
class GetCommandStatusResult:
    """Public command status view returned to external clients."""

    command_id: str
    type: str
    status: CommandStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class GetCommandStatus:
    """Fetch command status without mutating state or triggering processing."""

    def __init__(self, repository: CommandRepository) -> None:
        """Create the use case with the command repository port."""
        self.repository = repository

    def execute(self, request: GetCommandStatusRequest) -> GetCommandStatusResult:
        """Validate the id, load the command, and map it to a public status view."""
        command_id = self._validate_command_id(request.command_id)
        command = self.repository.get_by_id(command_id)
        if command is None:
            raise CommandStatusNotFoundError("command not found")

        return GetCommandStatusResult(
            command_id=command.id,
            type=command.type,
            status=command.status,
            created_at=command.created_at,
            started_at=command.started_at,
            completed_at=command.completed_at,
            error_message=command.error_message,
        )

    @staticmethod
    def _validate_command_id(command_id: str) -> str:
        """Return a normalized UUID string or raise a validation error."""
        try:
            return str(UUID(str(command_id)))
        except (TypeError, ValueError) as exc:
            raise InvalidCommandIdError("invalid command_id") from exc
