"""Application use case for worker-side command processing."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.handler_registry import HandlerRegistry, PipelineNotFoundError
from app.domain.context import CommandContext
from app.domain.ports import CommandRepository
from app.domain.status import CommandStatus


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

    def __init__(self, repository: CommandRepository, registry: HandlerRegistry) -> None:
        """Create the use case with command storage and handler registry."""
        self.repository = repository
        self.registry = registry

    def execute(self, request: ProcessCommandRequest) -> ProcessCommandResult:
        """Process one command id and always persist completed or failed status."""
        command = self.repository.get_by_id(request.command_id)
        if command is None:
            raise CommandNotFoundError(f"Command {request.command_id} not found")

        command.mark_processing()
        self.repository.update(command)

        try:
            pipeline = self.registry.get(command.type)
            context = pipeline.execute(CommandContext(command=command))
            if context.interrupted:
                command.mark_failed(context.error_summary())
            else:
                command.mark_completed()
        except PipelineNotFoundError as exc:
            command.mark_failed(str(exc))
        except Exception as exc:
            command.mark_failed(f"Handler execution failed: {exc}")

        self.repository.update(command)
        return ProcessCommandResult(command_id=command.id, status=command.status)
