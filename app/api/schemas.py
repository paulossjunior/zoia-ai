"""Pydantic schemas that define the public command submission contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubmitCommandRequest(BaseModel):
    """Request body for accepting a command into asynchronous processing."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "type": "TEST_COMMAND",
                    "payload": {"message": "hello"},
                }
            ]
        },
    )

    type: str = Field(
        min_length=1,
        description="Command type used by the worker registry to select a processing pipeline.",
        examples=["TEST_COMMAND"],
    )
    payload: dict[str, Any] = Field(
        description="Command-specific JSON object validated by the selected pipeline.",
        examples=[{"message": "hello"}],
    )

    @field_validator("type")
    @classmethod
    def type_must_not_be_blank(cls, value: str) -> str:
        """Reject blank command types before the command is accepted."""
        if not value.strip():
            raise ValueError("type is required")
        return value.strip()


class SubmitCommandResponse(BaseModel):
    """Acknowledgement returned after the command is stored for processing."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "command_id": "00000000-0000-4000-8000-000000000000",
                    "status": "queued",
                }
            ]
        }
    )

    command_id: str = Field(
        description="Unique identifier generated for tracking the accepted command.",
        examples=["00000000-0000-4000-8000-000000000000"],
    )
    status: str = Field(description="Initial command status.", examples=["queued"])


class CommandStatusResponse(BaseModel):
    """Complete read-only view of a command execution record."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "command_id": "00000000-0000-4000-8000-000000000000",
                    "type": "TEST_COMMAND",
                    "payload": {"message": "hello"},
                    "status": "completed",
                    "response": {"echo": "hello"},
                    "error_message": None,
                    "request_received_at": "2026-05-30T19:00:00Z",
                    "processing_started_at": "2026-05-30T19:00:01Z",
                    "processing_finished_at": "2026-05-30T19:00:02Z",
                }
            ]
        }
    )

    command_id: str = Field(
        description="Unique identifier generated when the command was submitted.",
        examples=["00000000-0000-4000-8000-000000000000"],
    )
    type: str = Field(description="Command type originally submitted.", examples=["TEST_COMMAND"])
    payload: dict[str, Any] = Field(description="Original command payload received during submission.")
    status: str = Field(
        description="Current command lifecycle status.",
        examples=["queued", "processing", "completed", "failed"],
    )
    response: dict[str, Any] | None = Field(default=None, description="Structured processing response when produced.")
    error_message: str | None = Field(default=None, description="Failure reason when status is failed.")
    request_received_at: datetime = Field(description="Timestamp when the command request was accepted.")
    processing_started_at: datetime | None = Field(default=None, description="Timestamp when worker processing started.")
    processing_finished_at: datetime | None = Field(default=None, description="Timestamp when processing completed or failed.")


class ErrorResponse(BaseModel):
    """Error body returned when command validation or lookup fails."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"detail": "invalid command request"},
                {"detail": "invalid command_id"},
                {"detail": "command not found"},
            ]
        }
    )

    detail: str = Field(description="Human-readable validation error summary.", examples=["invalid command request"])
