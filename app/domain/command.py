"""Command lifecycle entity used by application use cases and handlers.

The domain owns command state and timestamps only. External technologies are
kept outside this package and reach commands through application ports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.domain.status import CommandStatus


def utcnow() -> datetime:
    """Return a timezone-aware timestamp for command lifecycle events."""
    return datetime.now(timezone.utc)


@dataclass
class Command:
    """Command submitted for asynchronous processing.

    Commands begin queued, move to processing when a worker starts them, and
    end as completed or failed with a bounded error message.
    """

    id: str
    type: str
    payload: dict[str, Any]
    status: CommandStatus = CommandStatus.QUEUED
    created_at: datetime = field(default_factory=utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    response: dict[str, Any] | None = None

    @property
    def request_received_at(self) -> datetime:
        """Timestamp when the command request was accepted."""
        return self.created_at

    @request_received_at.setter
    def request_received_at(self, value: datetime) -> None:
        """Keep the public persistence name compatible with existing internals."""
        self.created_at = value

    @property
    def processing_started_at(self) -> datetime | None:
        """Timestamp when worker processing started."""
        return self.started_at

    @processing_started_at.setter
    def processing_started_at(self, value: datetime | None) -> None:
        """Keep the public persistence name compatible with existing internals."""
        self.started_at = value

    @property
    def processing_finished_at(self) -> datetime | None:
        """Timestamp when worker processing completed or failed."""
        return self.completed_at

    @processing_finished_at.setter
    def processing_finished_at(self, value: datetime | None) -> None:
        """Keep the public persistence name compatible with existing internals."""
        self.completed_at = value

    def mark_processing(self) -> None:
        """Mark the command as being handled and clear previous outcomes."""
        self.status = CommandStatus.PROCESSING
        self.started_at = utcnow()
        self.completed_at = None
        self.error_message = None
        self.response = None

    def mark_completed(self, response: dict[str, Any] | None = None) -> None:
        """Mark the command as successfully finished with an optional response."""
        self.status = CommandStatus.COMPLETED
        self.completed_at = utcnow()
        self.error_message = None
        self.response = response

    def mark_failed(self, error_message: str) -> None:
        """Mark the command as failed with a safe, traceable error message."""
        self.status = CommandStatus.FAILED
        self.completed_at = utcnow()
        self.error_message = safe_error_message(error_message)
        self.response = None


def safe_error_message(message: str) -> str:
    """Normalize handler errors before storing them on the command."""
    text = str(message).strip() or "Command processing failed"
    return text[:500]
