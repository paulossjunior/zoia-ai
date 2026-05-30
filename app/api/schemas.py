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
                    "external_id": "BOLSISTA-12345",
                    "callback": "https://sistema-origem.com/api/callback",
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
    external_id: str | None = Field(
        default=None,
        description="Optional source-system business identifier. Values are not unique.",
        examples=["BOLSISTA-12345"],
    )
    callback: str | None = Field(
        default=None,
        description="Optional callback URL. Missing, null, or blank values mean no callback is required.",
        examples=["https://sistema-origem.com/api/callback"],
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


class CommandDetailResponse(BaseModel):
    """Complete read-only view of a command execution record."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "command_id": "00000000-0000-4000-8000-000000000000",
                    "type": "TEST_COMMAND",
                    "external_id": "BOLSISTA-12345",
                    "callback": "https://sistema-origem.com/api/callback",
                    "payload": {"message": "hello"},
                    "status": "completed",
                    "response_payload": {"echo": "hello"},
                    "error_message": None,
                    "callback_status": "sent",
                    "callback_error_message": None,
                    "request_received_at": "2026-05-30T19:00:00Z",
                    "processing_started_at": "2026-05-30T19:00:01Z",
                    "processing_finished_at": "2026-05-30T19:00:02Z",
                    "callback_sent_at": "2026-05-30T19:00:03Z",
                }
            ]
        }
    )

    command_id: str = Field(
        description="Unique identifier generated when the command was submitted.",
        examples=["00000000-0000-4000-8000-000000000000"],
    )
    type: str = Field(description="Command type originally submitted.", examples=["TEST_COMMAND"])
    external_id: str | None = Field(default=None, description="Optional source-system business identifier.")
    callback: str | None = Field(default=None, description="Optional callback URL supplied during submission.")
    payload: dict[str, Any] = Field(description="Original command payload received during submission.")
    status: str = Field(
        description="Current command lifecycle status.",
        examples=["queued", "processing", "completed", "failed"],
    )
    response_payload: dict[str, Any] | None = Field(default=None, description="Structured processing response when produced.")
    error_message: str | None = Field(default=None, description="Failure reason when status is failed.")
    callback_status: str = Field(description="Current callback delivery status.")
    callback_error_message: str | None = Field(default=None, description="Callback failure reason when delivery fails.")
    request_received_at: datetime = Field(description="Timestamp when the command request was accepted.")
    processing_started_at: datetime | None = Field(default=None, description="Timestamp when worker processing started.")
    processing_finished_at: datetime | None = Field(default=None, description="Timestamp when processing completed or failed.")
    callback_sent_at: datetime | None = Field(default=None, description="Timestamp when callback delivery succeeded.")


class CommandStatusResponse(BaseModel):
    """Lightweight read-only view of a command status."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "command_id": "00000000-0000-4000-8000-000000000000",
                    "status": "processing",
                    "callback_status": "pending",
                }
            ]
        }
    )

    command_id: str = Field(description="Unique identifier generated when the command was submitted.")
    status: str = Field(description="Current command lifecycle status.", examples=["queued", "processing", "completed", "failed"])
    callback_status: str = Field(description="Current callback delivery status.", examples=["not_required", "pending", "sent", "failed"])


class CommandSummaryResponse(BaseModel):
    """Compact command view used in list responses."""

    id: str = Field(description="Unique identifier generated when the command was submitted.")
    type: str = Field(description="Command type originally submitted.")
    status: str = Field(description="Current command lifecycle status.")


class CommandListResponse(BaseModel):
    """Paginated command summary response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {"id": "1", "type": "SEND_EMAIL", "status": "failed"},
                        {"id": "2", "type": "GENERATE_REPORT", "status": "failed"},
                    ],
                    "total": 2,
                    "page": 1,
                    "page_size": 20,
                }
            ]
        }
    )

    items: list[CommandSummaryResponse] = Field(description="Command summaries on the current page.")
    total: int = Field(description="Total number of commands matching the filter.")
    page: int = Field(description="Current page number.")
    page_size: int = Field(description="Requested page size.")


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
