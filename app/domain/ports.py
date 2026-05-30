"""Application ports that keep command use cases decoupled from adapters."""

from __future__ import annotations

from typing import Any, Protocol

from app.domain.command import Command
from app.domain.context import CommandContext
from app.domain.status import CommandStatus


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

    def list(
        self,
        status: CommandStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Command], int]:
        """Return a page of commands and the total count for an optional status."""
        ...

    def get_latest_by_external_id(self, external_id: str) -> Command | None:
        """Load the most recent command for a non-unique external business id."""
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


class CallbackClient(Protocol):
    """Outbound callback delivery contract used after command processing ends."""

    def send(self, url: str, payload: dict[str, Any]) -> None:
        """Deliver a callback payload or raise a clear delivery error."""
        ...
