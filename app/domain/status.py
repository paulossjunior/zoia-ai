"""Explicit command lifecycle states owned by the domain model."""

from enum import StrEnum


class CommandStatus(StrEnum):
    """Allowed states for every command from submission to final outcome."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CallbackStatus(StrEnum):
    """Allowed states for optional callback delivery after processing."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
