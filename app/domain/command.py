"""Command lifecycle entity used by application use cases and handlers.

The domain owns command state and timestamps only. External technologies are
kept outside this package and reach commands through application ports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.domain.status import CallbackStatus, CommandStatus


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
    external_id: str | None = None
    callback: str | None = None
    created_at: datetime = field(default_factory=utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    response_payload: dict[str, Any] | None = None
    callback_status: CallbackStatus | None = None
    callback_error_message: str | None = None
    retry_count: int = 0
    callback_sent_at: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize callback tracking from the optional callback URL."""
        self.callback = normalize_optional_text(self.callback)
        self.external_id = normalize_optional_text(self.external_id)
        if self.callback_status is None:
            self.callback_status = CallbackStatus.PENDING if self.callback else CallbackStatus.NOT_REQUIRED
        elif isinstance(self.callback_status, str):
            self.callback_status = CallbackStatus(self.callback_status)

    @property
    def response(self) -> dict[str, Any] | None:
        """Backward-compatible alias for the persisted response payload."""
        return self.response_payload

    @response.setter
    def response(self, value: dict[str, Any] | None) -> None:
        """Backward-compatible alias for the persisted response payload."""
        self.response_payload = value

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
        self.response_payload = None

    def mark_completed(self, response: dict[str, Any] | None = None) -> None:
        """Mark the command as successfully finished with an optional response."""
        self.status = CommandStatus.COMPLETED
        self.completed_at = utcnow()
        self.error_message = None
        self.response_payload = response

    def mark_failed(self, error_message: str) -> None:
        """Mark the command as failed with a safe, traceable error message."""
        self.status = CommandStatus.FAILED
        self.completed_at = utcnow()
        self.error_message = safe_error_message(error_message)
        self.response_payload = None

    def callback_required(self) -> bool:
        """Return whether an outbound callback should be attempted."""
        return self.callback_status == CallbackStatus.PENDING and self.callback is not None

    def mark_callback_sent(self) -> None:
        """Record a successful callback delivery."""
        self.callback_status = CallbackStatus.SENT
        self.callback_error_message = None
        self.callback_sent_at = utcnow()
        self.retry_count += 1

    def mark_callback_failed(self, error_message: str) -> None:
        """Record a failed callback delivery without changing processing status."""
        self.callback_status = CallbackStatus.FAILED
        self.callback_error_message = safe_error_message(error_message)
        self.retry_count += 1


def safe_error_message(message: str) -> str:
    """Normalize handler errors before storing them on the command."""
    text = str(message).strip() or "Command processing failed"
    return text[:500]


def normalize_optional_text(value: str | None) -> str | None:
    """Normalize optional external identifiers and callback URLs."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None
