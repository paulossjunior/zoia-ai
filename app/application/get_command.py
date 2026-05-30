"""Read-only use case for retrieving a complete command record."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.ports import CommandRepository
from app.domain.status import CommandStatus


class InvalidCommandIdError(ValueError):
    """Raised when a detail lookup receives a malformed command id."""

    pass


class CommandNotFoundError(Exception):
    """Raised when no command exists for a valid lookup id."""

    pass


@dataclass(frozen=True)
class GetCommandRequest:
    """Input contract for reading complete command details by id."""

    command_id: str


@dataclass(frozen=True)
class GetCommandResult:
    """Complete command execution record returned to external clients."""

    command_id: str
    type: str
    status: CommandStatus
    payload: dict[str, Any]
    external_id: str | None
    callback: str | None
    response_payload: dict[str, Any] | None
    error_message: str | None
    callback_status: object
    callback_error_message: str | None
    request_received_at: datetime
    processing_started_at: datetime | None
    processing_finished_at: datetime | None
    callback_sent_at: datetime | None

    @property
    def id(self) -> str:
        """Backward-compatible alias for previous application tests."""
        return self.command_id

    @property
    def response(self) -> dict[str, Any] | None:
        """Backward-compatible alias for previous application tests."""
        return self.response_payload


class GetCommand:
    """Fetch a complete command record without mutating state."""

    def __init__(self, repository: CommandRepository) -> None:
        """Create the use case with the command repository port."""
        self.repository = repository

    def execute(self, request: GetCommandRequest) -> GetCommandResult:
        """Validate the id, load the command, and map it to a public record."""
        command_id = _validate_command_id(request.command_id)
        command = self.repository.get_by_id(command_id)
        if command is None:
            raise CommandNotFoundError("command not found")

        return GetCommandResult(
            command_id=command.id,
            type=command.type,
            status=command.status,
            payload=command.payload,
            external_id=command.external_id,
            callback=command.callback,
            response_payload=command.response_payload,
            error_message=command.error_message,
            callback_status=command.callback_status,
            callback_error_message=command.callback_error_message,
            request_received_at=command.request_received_at,
            processing_started_at=command.processing_started_at,
            processing_finished_at=command.processing_finished_at,
            callback_sent_at=command.callback_sent_at,
        )


def _validate_command_id(command_id: str) -> str:
    """Return a normalized UUID string or raise a validation error."""
    try:
        return str(UUID(str(command_id)))
    except (TypeError, ValueError) as exc:
        raise InvalidCommandIdError("invalid command_id") from exc
