"""Base domain handlers used to compose command processing chains."""

from __future__ import annotations

from app.domain.context import CommandContext


class BaseCommandHandler:
    """Base class for handlers that operate on a command context."""

    def handle(self, context: CommandContext) -> None:
        """Execute one handler responsibility."""
        raise NotImplementedError


class RecordingHandler(BaseCommandHandler):
    """Test helper handler that records execution order in context metadata."""

    def __init__(self, name: str) -> None:
        """Create a handler that records the provided name."""
        self.name = name

    def handle(self, context: CommandContext) -> None:
        """Append this handler name to the context handler order."""
        context.metadata.setdefault("handler_order", []).append(self.name)
