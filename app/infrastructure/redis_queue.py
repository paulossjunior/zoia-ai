"""Queue adapter that serializes command identifiers to Redis lists."""

from __future__ import annotations

import json
import logging
import os
from typing import Any


logger = logging.getLogger(__name__)


class RedisCommandQueue:
    """Redis-backed implementation of the command queue port."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        queue_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        """Create the adapter from explicit values, environment, or test client."""
        self.queue_name = queue_name or os.getenv("REDIS_QUEUE_NAME", "commands")
        if client is not None:
            self.client = client
        else:
            from redis import Redis

            self.client = Redis(
                host=host or os.getenv("REDIS_HOST", "localhost"),
                port=port or int(os.getenv("REDIS_PORT", "6379")),
                decode_responses=True,
            )

    def publish(self, command_id: str) -> None:
        """Publish a stored command id as a JSON message."""
        self.client.rpush(self.queue_name, json.dumps({"command_id": command_id}))

    def consume(self, timeout: int = 0) -> str | None:
        """Consume one JSON message and return its command id when valid."""
        item = self.client.blpop(self.queue_name, timeout=timeout)
        if item is None:
            return None
        raw = item[1] if isinstance(item, (tuple, list)) else item
        try:
            payload = json.loads(raw)
            command_id = payload.get("command_id")
            if not isinstance(command_id, str) or not command_id:
                raise ValueError("command_id is required")
            return command_id
        except Exception:
            logger.exception("Failed to decode command queue message")
            return None
