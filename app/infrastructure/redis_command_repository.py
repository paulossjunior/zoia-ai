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
            "response": command.response,
            "error_message": command.error_message,
            "request_received_at": command.request_received_at.isoformat(),
            "processing_started_at": command.processing_started_at.isoformat() if command.processing_started_at else None,
            "processing_finished_at": command.processing_finished_at.isoformat() if command.processing_finished_at else None,
        }

    @staticmethod
    def _from_dict(data: dict[str, Any]) -> Command:
        """Rehydrate a command entity from stored JSON data."""
        return Command(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            status=CommandStatus(data["status"]),
            created_at=datetime.fromisoformat(data.get("request_received_at") or data["created_at"]),
            started_at=_parse_optional_datetime(data.get("processing_started_at") or data.get("started_at")),
            completed_at=_parse_optional_datetime(data.get("processing_finished_at") or data.get("completed_at")),
            error_message=data.get("error_message"),
            response=data.get("response"),
        )


def _parse_optional_datetime(value: str | None) -> datetime | None:
    """Parse an optional ISO timestamp from Redis storage."""
    return datetime.fromisoformat(value) if value else None
