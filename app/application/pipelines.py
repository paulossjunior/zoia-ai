"""Pipeline executors for Chain of Responsibility command handling."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.context import CommandContext
from app.domain.ports import CommandHandler


class SequentialCommandPipeline:
    """Run command handlers in order until one records a blocking error."""

    def __init__(self, handlers: Iterable[CommandHandler]) -> None:
        """Create a pipeline from an ordered iterable of handlers."""
        self.handlers = list(handlers)

    def execute(self, context: CommandContext) -> CommandContext:
        """Execute handlers with a shared context and stop on interruption."""
        for handler in self.handlers:
            if context.interrupted:
                break
            handler.handle(context)
        return context
