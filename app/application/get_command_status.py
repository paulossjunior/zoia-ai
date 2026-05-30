"""Read-only use case for querying command lifecycle status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
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
    """Complete command execution record returned to external clients."""

    command_id: str
    type: str
    payload: dict[str, Any]
    status: CommandStatus
    response: dict[str, Any] | None
    error_message: str | None
    request_received_at: datetime
    processing_started_at: datetime | None
    processing_finished_at: datetime | None

    @property
    def created_at(self) -> datetime:
        """Backward-compatible alias for request receipt time."""
        return self.request_received_at

    @property
    def started_at(self) -> datetime | None:
        """Backward-compatible alias for processing start time."""
        return self.processing_started_at

    @property
    def completed_at(self) -> datetime | None:
        """Backward-compatible alias for processing finish time."""
        return self.processing_finished_at


class GetCommandStatus:
    """Fetch command status without mutating state or triggering processing."""

    def __init__(self, repository: CommandRepository) -> None:
        """Create the use case with the command repository port."""
        self.repository = repository

    def execute(self, request: GetCommandStatusRequest) -> GetCommandStatusResult:
        """Validate the id, load the command, and map it to a complete record."""
        command_id = self._validate_command_id(request.command_id)
        command = self.repository.get_by_id(command_id)
        if command is None:
            raise CommandStatusNotFoundError("command not found")

        return GetCommandStatusResult(
            command_id=command.id,
            type=command.type,
            payload=command.payload,
            status=command.status,
            response=command.response,
            error_message=command.error_message,
            request_received_at=command.request_received_at,
            processing_started_at=command.processing_started_at,
            processing_finished_at=command.processing_finished_at,
        )

    @staticmethod
    def _validate_command_id(command_id: str) -> str:
        """Return a normalized UUID string or raise a validation error."""
        try:
            return str(UUID(str(command_id)))
        except (TypeError, ValueError) as exc:
            raise InvalidCommandIdError("invalid command_id") from exc
