from __future__ import annotations

import json

from app.application.handler_registry import HandlerRegistry
from app.application.process_command import ProcessCommand
from app.domain.command import Command
from app.domain.status import CommandStatus
from app.infrastructure.redis_queue import RedisCommandQueue
from app.worker.main import process_one


class FakeRedis:
    def __init__(self) -> None:
        self.items: list[str] = []

    def rpush(self, queue_name: str, value: str) -> None:
        self.items.append(value)

    def blpop(self, queue_name: str, timeout: int = 0):
        return (queue_name, self.items.pop(0)) if self.items else None


def test_worker_single_iteration_consumes_queue_and_invokes_processor(repository, queue, fake_pipeline) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"})
    repository.save(command)
    queue.to_consume.append("cmd-1")
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", fake_pipeline)

    processed = process_one(queue, ProcessCommand(repository, registry))

    assert processed is True
    saved = repository.get_by_id("cmd-1")
    assert saved.status == CommandStatus.COMPLETED
    assert saved.completed_at is not None
    assert saved.response == {"handler": "fake"}


def test_redis_queue_serializes_and_deserializes_command_ids() -> None:
    redis = FakeRedis()
    queue = RedisCommandQueue(queue_name="commands", client=redis)

    queue.publish("cmd-1")

    assert json.loads(redis.items[0]) == {"command_id": "cmd-1"}
    assert queue.consume(timeout=1) == "cmd-1"
