"""Explicit command lifecycle states owned by the domain model."""

from enum import StrEnum


class CommandStatus(StrEnum):
    """Allowed states for every command from submission to final outcome."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
