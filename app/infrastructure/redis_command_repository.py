"""Redis-backed command repository adapter for local runtime state."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from app.domain.command import Command
from app.domain.status import CommandStatus


class RedisCommandRepository:
    """Persist command lifecycle snapshots as JSON documents in Redis."""

    def __init__(self, host: str | None = None, port: int | None = None, client: Any | None = None) -> None:
        """Create the repository from explicit values, environment, or test client."""
        if client is not None:
            self.client = client
        else:
            from redis import Redis

            self.client = Redis(
                host=host or os.getenv("REDIS_HOST", "localhost"),
                port=port or int(os.getenv("REDIS_PORT", "6379")),
                decode_responses=True,
            )

    def save(self, command: Command) -> None:
        """Store a command snapshot by command id."""
        self.client.set(self._key(command.id), json.dumps(self._to_dict(command)))

    def get_by_id(self, command_id: str) -> Command | None:
        """Load and deserialize a command snapshot by id."""
        raw = self.client.get(self._key(command_id))
        if raw is None:
            return None
        return self._from_dict(json.loads(raw))

    def update(self, command: Command) -> None:
        """Replace the stored command snapshot with the latest state."""
        self.save(command)

    @staticmethod
    def _key(command_id: str) -> str:
        """Build the storage key for a command id."""
        return f"command:{command_id}"

    @staticmethod
    def _to_dict(command: Command) -> dict[str, Any]:
        """Convert a command entity into JSON-serializable data."""
        return {
            "id": command.id,
            "type": command.type,
            "payload": command.payload,
            "status": command.status.value,
            "created_at": command.created_at.isoformat(),
            "started_at": command.started_at.isoformat() if command.started_at else None,
            "completed_at": command.completed_at.isoformat() if command.completed_at else None,
            "error_message": command.error_message,
        }

    @staticmethod
    def _from_dict(data: dict[str, Any]) -> Command:
        """Rehydrate a command entity from stored JSON data."""
        return Command(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            status=CommandStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message"),
        )
