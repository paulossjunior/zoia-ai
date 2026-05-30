"""HTTP routes for accepting commands without executing their business logic."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Body, Path, Query, Request, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    CommandDetailResponse,
    CommandListResponse,
    CommandStatusResponse,
    CommandSummaryResponse,
    ErrorResponse,
    SubmitCommandRequest,
    SubmitCommandResponse,
)
from app.application.get_command import (
    CommandNotFoundError,
    GetCommand,
    GetCommandRequest,
    InvalidCommandIdError,
)
from app.application.get_command_by_external_id import (
    GetCommandByExternalId,
    GetCommandByExternalIdRequest,
    InvalidExternalIdError,
)
from app.application.get_command_status import (
    CommandStatusNotFoundError,
    GetCommandStatus,
    GetCommandStatusRequest,
)
from app.application.list_commands import (
    InvalidCommandStatusError,
    InvalidPaginationError,
    ListCommands,
    ListCommandsRequest,
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
    result = use_case.execute(
        UseCaseRequest(
            type=payload.type,
            payload=payload.payload,
            external_id=payload.external_id,
            callback=payload.callback,
        )
    )
    logger.info("command_submitted command_id=%s type=%s status=%s", result.command_id, payload.type, result.status.value)
    return SubmitCommandResponse(command_id=result.command_id, status=result.status.value)


@router.get(
    "/commands",
    response_model=CommandListResponse,
    status_code=status.HTTP_200_OK,
    summary="List commands",
    description=(
        "Returns paginated command summaries, optionally filtered by status. "
        "The operation is read-only and returns summaries without payloads, "
        "responses, or error details."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Command summaries found.",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {"id": "1", "type": "SEND_EMAIL", "status": "failed"},
                            {"id": "2", "type": "GENERATE_REPORT", "status": "failed"},
                        ],
                        "total": 2,
                        "page": 1,
                        "page_size": 20,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid status filter or pagination.",
            "content": {"application/json": {"examples": {"invalidStatus": {"value": {"detail": "invalid status"}}, "invalidPagination": {"value": {"detail": "invalid pagination"}}}}},
        },
    },
)
def list_commands(
    request: Request,
    status_filter: Annotated[
        str | None,
        Query(alias="status", description="Optional status filter: queued, processing, completed, or failed."),
    ] = None,
    page: Annotated[int, Query(description="Page number starting at 1.")] = 1,
    page_size: Annotated[int, Query(description="Number of items per page.")] = 20,
) -> CommandListResponse | JSONResponse:
    """Return paginated command summaries without queue or handler side effects."""
    use_case: ListCommands = request.app.state.list_commands
    try:
        result = use_case.execute(ListCommandsRequest(status=status_filter, page=page, page_size=page_size))
    except InvalidCommandStatusError:
        logger.info("command_list_invalid_status status=%s page=%s page_size=%s", status_filter, page, page_size)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "invalid status"})
    except InvalidPaginationError:
        logger.info("command_list_invalid_pagination status=%s page=%s page_size=%s", status_filter, page, page_size)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "invalid pagination"})

    logger.info("command_list status=%s page=%s page_size=%s total=%s", status_filter, result.page, result.page_size, result.total)
    return CommandListResponse(
        items=[
            CommandSummaryResponse(id=item.id, type=item.type, status=item.status.value)
            for item in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/commands/external/{external_id}",
    response_model=CommandDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get latest command by external id",
    description="Returns the most recent command associated with a source-system external id.",
    responses={
        status.HTTP_200_OK: {"description": "Latest command found."},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Invalid external id."},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Command not found."},
    },
)
def get_command_by_external_id(
    external_id: Annotated[str, Path(description="Source-system business identifier.")],
    request: Request,
) -> CommandDetailResponse | JSONResponse:
    """Return the newest command for an external id without scheduling work."""
    use_case: GetCommandByExternalId = request.app.state.get_command_by_external_id
    try:
        result = use_case.execute(GetCommandByExternalIdRequest(external_id=external_id))
    except InvalidExternalIdError:
        logger.info("command_external_lookup_invalid external_id=%s", external_id)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "invalid external_id"})
    except CommandNotFoundError:
        logger.info("command_external_lookup_not_found external_id=%s", external_id)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "command not found"})

    logger.info("command_external_lookup external_id=%s command_id=%s", external_id, result.command_id)
    return _detail_response(result)


@router.get(
    "/commands/{command_id}/status",
    response_model=CommandStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get command status",
    description="Returns only the current status for a previously submitted command. The operation is read-only.",
    responses={
        status.HTTP_200_OK: {
            "description": "Command status found.",
            "content": {"application/json": {"example": {"command_id": "00000000-0000-4000-8000-000000000000", "status": "processing", "callback_status": "pending"}}},
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
def get_command_status_only(
    command_id: Annotated[
        str,
        Path(description="UUID command identifier returned by POST /commands.", examples=["00000000-0000-4000-8000-000000000000"]),
    ],
    request: Request,
) -> CommandStatusResponse | JSONResponse:
    """Return only command id and status without enqueuing or processing work."""
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
        status=result.status.value,
        callback_status=result.callback_status.value,
    )


@router.get(
    "/commands/{command_id}",
    response_model=CommandDetailResponse,
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
                        "external_id": None,
                        "callback": None,
                        "payload": {"message": "hello"},
                        "status": "completed",
                        "response_payload": {"echo": "hello"},
                        "error_message": None,
                        "callback_status": "not_required",
                        "callback_error_message": None,
                        "request_received_at": "2026-05-30T19:00:00Z",
                        "processing_started_at": "2026-05-30T19:00:01Z",
                        "processing_finished_at": "2026-05-30T19:00:02Z",
                        "callback_sent_at": None,
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
def get_command(
    command_id: Annotated[
        str,
        Path(
            description="UUID command identifier returned by POST /commands.",
            examples=["00000000-0000-4000-8000-000000000000"],
        ),
    ],
    request: Request,
) -> CommandDetailResponse | JSONResponse:
    """Return a complete command record without enqueuing or processing work."""
    use_case: GetCommand = request.app.state.get_command
    try:
        result = use_case.execute(GetCommandRequest(command_id=command_id))
    except InvalidCommandIdError:
        logger.info("command_detail_lookup_invalid command_id=%s", command_id)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "invalid command_id"})
    except CommandNotFoundError:
        logger.info("command_detail_lookup_not_found command_id=%s", command_id)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "command not found"})

    logger.info("command_detail_lookup command_id=%s status=%s", result.command_id, result.status.value)
    return _detail_response(result)


def _detail_response(result) -> CommandDetailResponse:
    """Map application command detail results to the public HTTP schema."""
    return CommandDetailResponse(
        command_id=result.command_id,
        type=result.type,
        external_id=result.external_id,
        callback=result.callback,
        payload=result.payload,
        status=result.status.value,
        response_payload=result.response_payload,
        error_message=result.error_message,
        callback_status=result.callback_status.value,
        callback_error_message=result.callback_error_message,
        request_received_at=result.request_received_at,
        processing_started_at=result.processing_started_at,
        processing_finished_at=result.processing_finished_at,
        callback_sent_at=result.callback_sent_at,
    )
