"""Redis-backed command repository adapter for local runtime state."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from app.domain.command import Command
from app.domain.status import CallbackStatus, CommandStatus


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

    def list(
        self,
        status: CommandStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Command], int]:
        """Return commands filtered by status and ordered newest first."""
        commands: list[Command] = []
        for key in self.client.scan_iter(match="command:*"):
            raw = self.client.get(key)
            if raw is None:
                continue
            command = self._from_dict(json.loads(raw))
            if status is None or command.status == status:
                commands.append(command)
        commands.sort(key=lambda command: command.request_received_at, reverse=True)
        total = len(commands)
        start = (page - 1) * page_size
        end = start + page_size
        return commands[start:end], total

    def get_latest_by_external_id(self, external_id: str) -> Command | None:
        """Return the newest command for an external id from Redis snapshots."""
        commands: list[Command] = []
        for key in self.client.scan_iter(match="command:*"):
            raw = self.client.get(key)
            if raw is None:
                continue
            command = self._from_dict(json.loads(raw))
            if command.external_id == external_id:
                commands.append(command)
        commands.sort(key=lambda command: command.request_received_at, reverse=True)
        return commands[0] if commands else None

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
            "external_id": command.external_id,
            "callback": command.callback,
            "status": command.status.value,
            "response_payload": command.response_payload,
            "response": command.response_payload,
            "error_message": command.error_message,
            "callback_status": command.callback_status.value,
            "callback_error_message": command.callback_error_message,
            "retry_count": command.retry_count,
            "request_received_at": command.request_received_at.isoformat(),
            "processing_started_at": command.processing_started_at.isoformat() if command.processing_started_at else None,
            "processing_finished_at": command.processing_finished_at.isoformat() if command.processing_finished_at else None,
            "callback_sent_at": command.callback_sent_at.isoformat() if command.callback_sent_at else None,
        }

    @staticmethod
    def _from_dict(data: dict[str, Any]) -> Command:
        """Rehydrate a command entity from stored JSON data."""
        return Command(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            status=CommandStatus(data["status"]),
            external_id=data.get("external_id"),
            callback=data.get("callback"),
            created_at=datetime.fromisoformat(data.get("request_received_at") or data["created_at"]),
            started_at=_parse_optional_datetime(data.get("processing_started_at") or data.get("started_at")),
            completed_at=_parse_optional_datetime(data.get("processing_finished_at") or data.get("completed_at")),
            error_message=data.get("error_message"),
            response_payload=data.get("response_payload", data.get("response")),
            callback_status=CallbackStatus(data.get("callback_status", "not_required")),
            callback_error_message=data.get("callback_error_message"),
            retry_count=int(data.get("retry_count", 0)),
            callback_sent_at=_parse_optional_datetime(data.get("callback_sent_at")),
        )


def _parse_optional_datetime(value: str | None) -> datetime | None:
    """Parse an optional ISO timestamp from Redis storage."""
    return datetime.fromisoformat(value) if value else None
