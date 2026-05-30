"""Thread-safe in-memory command repository used by tests and local fixtures."""

from __future__ import annotations

from threading import RLock

from app.domain.command import Command


class MemoryCommandRepository:
    """Store command objects in process memory behind the repository port."""

    def __init__(self) -> None:
        """Create an empty repository protected by a lock."""
        self._commands: dict[str, Command] = {}
        self._lock = RLock()

    def save(self, command: Command) -> None:
        """Store a newly created command object."""
        with self._lock:
            self._commands[command.id] = command

    def get_by_id(self, command_id: str) -> Command | None:
        """Return a command by id, or None when it has not been stored."""
        with self._lock:
            return self._commands.get(command_id)

    def update(self, command: Command) -> None:
        """Persist the latest state for an existing command object."""
        with self._lock:
            self._commands[command.id] = command
