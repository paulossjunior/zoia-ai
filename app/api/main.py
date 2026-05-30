"""FastAPI application factory for the asynchronous command HTTP boundary."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.application.get_command_status import GetCommandStatus
from app.application.submit_command import InvalidCommandError, SubmitCommand
from app.infrastructure.logging import configure_logging
from app.infrastructure.memory_command_repository import MemoryCommandRepository
from app.infrastructure.redis_command_repository import RedisCommandRepository
from app.infrastructure.redis_queue import RedisCommandQueue


logger = logging.getLogger(__name__)


def create_app(repository: object | None = None, queue: object | None = None) -> FastAPI:
    """Create the API app with documentation metadata and command dependencies."""
    configure_logging()
    app = FastAPI(
        title="Async Command Processing API",
        description=(
            "HTTP API for submitting commands to be processed asynchronously. "
            "Clients receive a queued acknowledgement and do not wait for "
            "command business logic to run."
        ),
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "commands",
                "description": "Submit commands and receive immediate queued acknowledgements.",
            }
        ],
    )
    repo = repository or RedisCommandRepository()
    command_queue = queue or RedisCommandQueue()
    app.state.repository = repo
    app.state.queue = command_queue
    app.state.submit_command = SubmitCommand(repo, command_queue)
    app.state.get_command_status = GetCommandStatus(repo)

    def custom_openapi() -> dict[str, object]:
        """Generate OpenAPI schema aligned with the API's HTTP 400 validation contract."""
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )
        for path_item in schema["paths"].values():
            for operation in path_item.values():
                operation.get("responses", {}).pop("422", None)
        status_response = schema["paths"].get("/commands/{command_id}", {}).get("get", {}).get("responses", {}).get("200", {})
        status_example = status_response.get("content", {}).get("application/json", {}).get("example")
        if isinstance(status_example, dict):
            status_example["error_message"] = None
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Convert request parsing and schema validation errors into HTTP 400."""
        logger.info("command_validation_failed path=%s error=%s", request.url.path, exc.errors())
        return JSONResponse(status_code=400, content={"detail": "invalid command request"})

    @app.exception_handler(InvalidCommandError)
    async def invalid_command_handler(request: Request, exc: InvalidCommandError) -> JSONResponse:
        """Convert application-level command validation errors into HTTP 400."""
        logger.info("command_validation_failed path=%s error=%s", request.url.path, exc)
        return JSONResponse(status_code=400, content={"detail": "invalid command request"})

    app.include_router(router)
    return app


app = create_app()
