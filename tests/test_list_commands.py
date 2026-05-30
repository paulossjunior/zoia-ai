from __future__ import annotations

import json

import pytest

from app.application.list_commands import (
    InvalidCommandStatusError,
    InvalidPaginationError,
    ListCommands,
    ListCommandsRequest,
)
from app.domain.command import Command
from app.domain.status import CommandStatus
from app.infrastructure.memory_command_repository import MemoryCommandRepository
from app.infrastructure.redis_command_repository import RedisCommandRepository
from tests.conftest import make_command


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def scan_iter(self, match: str | None = None):
        return list(self.values)


def _repository_with_commands() -> MemoryCommandRepository:
    repository = MemoryCommandRepository()
    for command in [
        make_command("00000000-0000-4000-8000-000000000001", "queued"),
        make_command("00000000-0000-4000-8000-000000000002", "processing"),
        make_command("00000000-0000-4000-8000-000000000003", "completed"),
        make_command("00000000-0000-4000-8000-000000000004", "failed"),
        make_command("00000000-0000-4000-8000-000000000005", "failed", "SEND_EMAIL"),
    ]:
        repository.save(command)
    return repository


def test_list_commands_filters_by_each_status() -> None:
    repository = _repository_with_commands()
    use_case = ListCommands(repository)

    for status in CommandStatus:
        result = use_case.execute(ListCommandsRequest(status=status.value))
        assert all(item.status == status for item in result.items)
        assert result.total == len(result.items)


def test_list_commands_uses_default_pagination() -> None:
    result = ListCommands(_repository_with_commands()).execute(ListCommandsRequest())

    assert result.page == 1
    assert result.page_size == 20
    assert result.total == 5
    assert len(result.items) == 5


def test_list_commands_applies_explicit_pagination_and_out_of_range_page() -> None:
    use_case = ListCommands(_repository_with_commands())

    first_page = use_case.execute(ListCommandsRequest(page=1, page_size=2))
    third_page = use_case.execute(ListCommandsRequest(page=3, page_size=2))
    empty_page = use_case.execute(ListCommandsRequest(page=99, page_size=2))

    assert len(first_page.items) == 2
    assert len(third_page.items) == 1
    assert empty_page.items == []
    assert empty_page.total == 5


def test_list_commands_rejects_invalid_status_and_pagination() -> None:
    use_case = ListCommands(_repository_with_commands())

    with pytest.raises(InvalidCommandStatusError, match="invalid status"):
        use_case.execute(ListCommandsRequest(status="unknown"))
    with pytest.raises(InvalidPaginationError, match="invalid pagination"):
        use_case.execute(ListCommandsRequest(page=0))
    with pytest.raises(InvalidPaginationError, match="invalid pagination"):
        use_case.execute(ListCommandsRequest(page_size=0))


def test_memory_repository_lists_status_filtered_commands() -> None:
    repository = _repository_with_commands()

    commands, total = repository.list(status=CommandStatus.FAILED, page=1, page_size=20)

    assert total == 2
    assert {command.status for command in commands} == {CommandStatus.FAILED}


def test_redis_repository_lists_status_filtered_commands() -> None:
    redis = FakeRedis()
    repository = RedisCommandRepository(client=redis)
    for command in [
        make_command("00000000-0000-4000-8000-000000000001", "failed"),
        make_command("00000000-0000-4000-8000-000000000002", "completed"),
    ]:
        repository.save(command)

    commands, total = repository.list(status=CommandStatus.FAILED, page=1, page_size=20)

    assert total == 1
    assert commands[0].status == CommandStatus.FAILED
    assert json.loads(redis.values[f"command:{commands[0].id}"])["status"] == "failed"
