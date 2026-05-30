from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.get_command import CommandNotFoundError
from app.application.get_command_by_external_id import (
    GetCommandByExternalId,
    GetCommandByExternalIdRequest,
    InvalidExternalIdError,
)
from app.domain.command import Command
from app.infrastructure.memory_command_repository import MemoryCommandRepository


def test_get_command_by_external_id_returns_latest_command() -> None:
    repository = MemoryCommandRepository()
    older = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"version": 1}, external_id="EXT-1")
    newer = Command(id=str(uuid4()), type="TEST_COMMAND", payload={"version": 2}, external_id="EXT-1")
    older.request_received_at = newer.request_received_at - timedelta(seconds=10)
    repository.save(older)
    repository.save(newer)

    result = GetCommandByExternalId(repository).execute(GetCommandByExternalIdRequest(external_id="EXT-1"))

    assert result.command_id == newer.id
    assert result.external_id == "EXT-1"
    assert result.payload == {"version": 2}


def test_get_command_by_external_id_rejects_blank_id() -> None:
    with pytest.raises(InvalidExternalIdError, match="invalid external_id"):
        GetCommandByExternalId(MemoryCommandRepository()).execute(GetCommandByExternalIdRequest(external_id=" "))


def test_get_command_by_external_id_unknown_raises_not_found() -> None:
    with pytest.raises(CommandNotFoundError, match="command not found"):
        GetCommandByExternalId(MemoryCommandRepository()).execute(GetCommandByExternalIdRequest(external_id="EXT-404"))
