from __future__ import annotations

import pytest

from app.application.pipelines import SequentialCommandPipeline
from app.domain.command import Command
from app.domain.context import CommandContext
from app.infrastructure.memory_command_repository import MemoryCommandRepository


class FakeQueue:
    def __init__(self) -> None:
        self.published: list[str] = []
        self.to_consume: list[str] = []

    def publish(self, command_id: str) -> None:
        self.published.append(command_id)

    def consume(self, timeout: int = 0) -> str | None:
        return self.to_consume.pop(0) if self.to_consume else None


class FakeHandler:
    def __init__(self, name: str, fail: bool = False, raise_error: bool = False) -> None:
        self.name = name
        self.fail = fail
        self.raise_error = raise_error

    def handle(self, context: CommandContext) -> None:
        if self.raise_error:
            raise RuntimeError(f"{self.name} exploded")
        context.metadata.setdefault("handler_order", []).append(self.name)
        if self.fail:
            context.add_error(f"{self.name} failed")
        else:
            context.result = {"handler": self.name}


@pytest.fixture
def repository() -> MemoryCommandRepository:
    return MemoryCommandRepository()


@pytest.fixture
def queue() -> FakeQueue:
    return FakeQueue()


@pytest.fixture
def sample_payload() -> dict[str, str]:
    return {"message": "hello"}


@pytest.fixture
def fake_pipeline() -> SequentialCommandPipeline:
    return SequentialCommandPipeline([FakeHandler("fake")])


def make_command(command_id: str, status: str = "queued", command_type: str = "TEST_COMMAND") -> Command:
    """Create a command fixture in the requested lifecycle state."""
    command = Command(id=command_id, type=command_type, payload={"message": command_id})
    if status == "processing":
        command.mark_processing()
    elif status == "completed":
        command.mark_processing()
        command.mark_completed({"echo": command_id})
    elif status == "failed":
        command.mark_processing()
        command.mark_failed(f"{command_id} failed")
    return command
