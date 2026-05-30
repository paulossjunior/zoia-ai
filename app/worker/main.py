"""Worker entrypoint that consumes queued command ids and processes them."""

from __future__ import annotations

import logging
import time

from app.application.handler_registry import create_default_registry
from app.application.process_command import CommandNotFoundError, ProcessCommand, ProcessCommandRequest
from app.infrastructure.http_callback_client import HttpCallbackClient
from app.infrastructure.logging import configure_logging
from app.infrastructure.postgres_command_repository import PostgresCommandRepository
from app.infrastructure.redis_queue import RedisCommandQueue


logger = logging.getLogger(__name__)


def create_worker_dependencies() -> tuple[PostgresCommandRepository, RedisCommandQueue, ProcessCommand]:
    """Compose runtime adapters, registry, and processing use case."""
    repository = PostgresCommandRepository()
    queue = RedisCommandQueue()
    registry = create_default_registry()
    callback_client = HttpCallbackClient()
    return repository, queue, ProcessCommand(repository, registry, callback_client)


def process_one(queue: object, processor: ProcessCommand, timeout: int = 0) -> bool:
    """Consume and process a single command id, logging failures explicitly."""
    command_id = queue.consume(timeout=timeout)
    if command_id is None:
        return False
    logger.info("command_processing_started command_id=%s", command_id)
    try:
        result = processor.execute(ProcessCommandRequest(command_id=command_id))
        logger.info("command_processing_finished command_id=%s status=%s", result.command_id, result.status.value)
    except CommandNotFoundError:
        logger.exception("command_processing_failed command_id=%s reason=not_found", command_id)
    except Exception:
        logger.exception("command_processing_failed command_id=%s", command_id)
    return True


def run_forever(queue: object, processor: ProcessCommand) -> None:
    """Continuously poll for commands while leaving type logic to the registry."""
    while True:
        process_one(queue, processor, timeout=5)
        time.sleep(0.1)


def main() -> None:
    """Start the command worker process."""
    configure_logging()
    _repository, queue, processor = create_worker_dependencies()
    run_forever(queue, processor)


if __name__ == "__main__":
    main()
