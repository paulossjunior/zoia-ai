"""Application ports that keep command use cases decoupled from adapters."""

from __future__ import annotations

from typing import Protocol

from app.domain.command import Command
from app.domain.context import CommandContext


class CommandRepository(Protocol):
    """Persistence contract for storing and updating command lifecycle state."""

    def save(self, command: Command) -> None:
        """Store a newly accepted command before it is published for processing."""
        ...

    def get_by_id(self, command_id: str) -> Command | None:
        """Load a command by identifier for worker processing."""
        ...

    def update(self, command: Command) -> None:
        """Persist status, timestamp, result, or error changes for a command."""
        ...


class CommandQueue(Protocol):
    """Queue contract for publishing and consuming command identifiers."""

    def publish(self, command_id: str) -> None:
        """Publish a command identifier after the command has been stored."""
        ...

    def consume(self, timeout: int = 0) -> str | None:
        """Return the next command identifier, or None when no work is available."""
        ...


class CommandHandler(Protocol):
    """Single responsibility step in a command processing chain."""

    def handle(self, context: CommandContext) -> None:
        """Handle the command context and optionally add blocking errors."""
        ...


class CommandPipeline(Protocol):
    """Executable chain for one command type."""

    def execute(self, context: CommandContext) -> CommandContext:
        """Run handlers and return the shared context with result or errors."""
        ...
