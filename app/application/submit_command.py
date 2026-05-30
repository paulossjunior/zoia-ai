"""Application use case for accepting and enqueueing command submissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.domain.command import Command
from app.domain.ports import CommandQueue, CommandRepository
from app.domain.status import CommandStatus


class InvalidCommandError(ValueError):
    """Raised when the command envelope is missing required submission data."""

    pass


@dataclass(frozen=True)
class SubmitCommandRequest:
    """Input contract for submitting a command to asynchronous processing."""

    type: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class SubmitCommandResult:
    """Acknowledgement returned after a command is stored and queued."""

    command_id: str
    status: CommandStatus


class SubmitCommand:
    """Validate, persist, and enqueue a command without executing business work."""

    def __init__(self, repository: CommandRepository, queue: CommandQueue) -> None:
        """Create the use case with storage and queue ports."""
        self.repository = repository
        self.queue = queue

    def execute(self, request: SubmitCommandRequest) -> SubmitCommandResult:
        """Store a queued command, publish its id, and return the acknowledgement."""
        command_type = self._validate_type(request.type)
        payload = self._validate_payload(request.payload)
        command = Command(id=str(uuid4()), type=command_type, payload=payload)

        self.repository.save(command)
        self.queue.publish(command.id)

        return SubmitCommandResult(command_id=command.id, status=command.status)

    @staticmethod
    def _validate_type(command_type: str) -> str:
        """Normalize and validate the required command type."""
        if not isinstance(command_type, str) or not command_type.strip():
            raise InvalidCommandError("type is required")
        return command_type.strip()

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """Validate that payload is an object before queue publication."""
        if not isinstance(payload, dict):
            raise InvalidCommandError("payload must be an object")
        return payload
