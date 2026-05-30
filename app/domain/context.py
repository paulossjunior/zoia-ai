"""Shared execution context passed through command handler chains."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.command import Command


@dataclass
class CommandContext:
    """Mutable state shared by handlers while processing one command."""

    command: Command
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    result: dict[str, Any] | None = None

    @property
    def interrupted(self) -> bool:
        """Return true when a handler added an error and the chain should stop."""
        return bool(self.errors)

    def add_error(self, message: str) -> None:
        """Record a blocking handler error on the context."""
        self.errors.append(str(message))

    def error_summary(self) -> str:
        """Combine context errors for storage on a failed command."""
        return "; ".join(self.errors) if self.errors else ""
