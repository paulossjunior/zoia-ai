"""Application use case for worker-side command processing."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from app.application.handler_registry import HandlerRegistry, PipelineNotFoundError
from app.domain.context import CommandContext
from app.domain.ports import CallbackClient, CommandRepository
from app.domain.status import CommandStatus


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessCommandRequest:
    """Input contract containing the command identifier consumed by a worker."""

    command_id: str


@dataclass(frozen=True)
class ProcessCommandResult:
    """Processing result with the command's final tracked status."""

    command_id: str
    status: CommandStatus


class CommandNotFoundError(Exception):
    """Raised when consumed work references a command that cannot be loaded."""

    pass


class ProcessCommand:
    """Load a command, run its registered pipeline, and persist the outcome."""

    def __init__(
        self,
        repository: CommandRepository,
        registry: HandlerRegistry,
        callback_client: CallbackClient | None = None,
    ) -> None:
        """Create the use case with command storage and handler registry."""
        self.repository = repository
        self.registry = registry
        self.callback_client = callback_client

    def execute(self, request: ProcessCommandRequest) -> ProcessCommandResult:
        """Process one command id and always persist completed or failed status."""
        command = self.repository.get_by_id(request.command_id)
        if command is None:
            raise CommandNotFoundError(f"Command {request.command_id} not found")

        command.mark_processing()
        self.repository.update(command)
        logger.info("command_processing_started command_id=%s type=%s", command.id, command.type)

        try:
            pipeline = self.registry.get(command.type)
            context = pipeline.execute(CommandContext(command=command))
            if context.interrupted:
                command.mark_failed(context.error_summary())
            else:
                command.mark_completed(response=context.result)
        except PipelineNotFoundError as exc:
            command.mark_failed(str(exc))
        except Exception as exc:
            command.mark_failed(f"Handler execution failed: {exc}")

        self.repository.update(command)
        if command.status == CommandStatus.COMPLETED:
            logger.info("command_processing_completed command_id=%s type=%s", command.id, command.type)
        else:
            logger.error(
                "command_processing_failed command_id=%s type=%s error=%s",
                command.id,
                command.type,
                command.error_message,
            )
        self._deliver_callback(command)
        return ProcessCommandResult(command_id=command.id, status=command.status)

    def _deliver_callback(self, command) -> None:
        """Attempt the optional post-processing callback and persist its audit state."""
        if not command.callback_required():
            return
        if self.callback_client is None:
            command.mark_callback_failed("Callback client is not configured")
            self.repository.update(command)
            logger.error("command_callback_failed command_id=%s error=%s", command.id, command.callback_error_message)
            return

        logger.info("command_callback_attempt command_id=%s callback=%s", command.id, command.callback)
        try:
            self.callback_client.send(command.callback, build_callback_payload(command))
        except Exception as exc:
            command.mark_callback_failed(str(exc))
            logger.error("command_callback_failed command_id=%s error=%s", command.id, command.callback_error_message)
        else:
            command.mark_callback_sent()
            logger.info("command_callback_sent command_id=%s", command.id)
        self.repository.update(command)


def build_callback_payload(command) -> dict[str, Any]:
    """Build the public callback payload for success or failure outcomes."""
    payload: dict[str, Any] = {"status": command.status.value}
    if command.external_id:
        payload["external_id"] = command.external_id
    if command.status == CommandStatus.COMPLETED:
        payload["payload"] = command.response_payload or {}
    else:
        payload["payload"] = {"message": command.error_message or "Command processing failed"}
    return payload
