"""HTTP routes for accepting commands without executing their business logic."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Body, Path, Request, status
from fastapi.responses import JSONResponse

from app.api.schemas import CommandStatusResponse, ErrorResponse, SubmitCommandRequest, SubmitCommandResponse
from app.application.get_command_status import (
    CommandStatusNotFoundError,
    GetCommandStatus,
    GetCommandStatusRequest,
    InvalidCommandIdError,
)
from app.application.submit_command import SubmitCommand, SubmitCommandRequest as UseCaseRequest


logger = logging.getLogger(__name__)
router = APIRouter(tags=["commands"])


@router.post(
    "/commands",
    response_model=SubmitCommandResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit command",
    description=(
        "Accepts a command for asynchronous processing. The request validates "
        "the command envelope, stores the command, schedules it for background "
        "execution, and returns immediately with queued status."
    ),
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "Command accepted for asynchronous processing.",
            "content": {
                "application/json": {
                    "example": {
                        "command_id": "00000000-0000-4000-8000-000000000000",
                        "status": "queued",
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid command submission.",
            "content": {"application/json": {"example": {"detail": "invalid command request"}}},
        },
    },
)
def submit_command(
    payload: Annotated[
        SubmitCommandRequest,
        Body(
            openapi_examples={
                "testCommand": {
                    "summary": "TEST_COMMAND example",
                    "description": "Valid command envelope accepted for asynchronous processing.",
                    "value": {"type": "TEST_COMMAND", "payload": {"message": "hello"}},
                }
            }
        ),
    ],
    request: Request,
) -> SubmitCommandResponse:
    """Validate, store, and schedule a command through the application use case."""
    use_case: SubmitCommand = request.app.state.submit_command
    result = use_case.execute(UseCaseRequest(type=payload.type, payload=payload.payload))
    logger.info("command_submitted command_id=%s type=%s status=%s", result.command_id, payload.type, result.status.value)
    return SubmitCommandResponse(command_id=result.command_id, status=result.status.value)


@router.get(
    "/commands/{command_id}",
    response_model=CommandStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get command record",
    description=(
        "Returns the complete persisted execution record for a previously "
        "submitted command. The operation is read-only, does not schedule work, "
        "and includes the original payload, current status, response or error, "
        "and lifecycle timestamps."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Command status found.",
            "content": {
                "application/json": {
                    "example": {
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
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid command identifier.",
            "content": {"application/json": {"example": {"detail": "invalid command_id"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Command not found.",
            "content": {"application/json": {"example": {"detail": "command not found"}}},
        },
    },
)
def get_command_status(
    command_id: Annotated[
        str,
        Path(
            description="UUID command identifier returned by POST /commands.",
            examples=["00000000-0000-4000-8000-000000000000"],
        ),
    ],
    request: Request,
) -> CommandStatusResponse | JSONResponse:
    """Return a complete command record without enqueuing or processing work."""
    use_case: GetCommandStatus = request.app.state.get_command_status
    try:
        result = use_case.execute(GetCommandStatusRequest(command_id=command_id))
    except InvalidCommandIdError:
        logger.info("command_status_lookup_invalid command_id=%s", command_id)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "invalid command_id"})
    except CommandStatusNotFoundError:
        logger.info("command_status_lookup_not_found command_id=%s", command_id)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "command not found"})

    logger.info("command_status_lookup command_id=%s status=%s", result.command_id, result.status.value)
    return CommandStatusResponse(
        command_id=result.command_id,
        type=result.type,
        payload=result.payload,
        status=result.status.value,
        response=result.response,
        error_message=result.error_message,
        request_received_at=result.request_received_at,
        processing_started_at=result.processing_started_at,
        processing_finished_at=result.processing_finished_at,
    )
