"""Thread-safe in-memory command repository used by tests and local fixtures."""

from __future__ import annotations

from threading import RLock

from app.domain.command import Command
from app.domain.status import CommandStatus


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

    def list(
        self,
        status: CommandStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Command], int]:
        """Return commands filtered by status and ordered newest first."""
        with self._lock:
            commands = list(self._commands.values())
        if status is not None:
            commands = [command for command in commands if command.status == status]
        commands.sort(key=lambda command: command.request_received_at, reverse=True)
        total = len(commands)
        start = (page - 1) * page_size
        end = start + page_size
        return commands[start:end], total

    def get_latest_by_external_id(self, external_id: str) -> Command | None:
        """Return the newest command for an external id, or None when absent."""
        with self._lock:
            commands = [
                command
                for command in self._commands.values()
                if command.external_id == external_id
            ]
        commands.sort(key=lambda command: command.request_received_at, reverse=True)
        return commands[0] if commands else None
