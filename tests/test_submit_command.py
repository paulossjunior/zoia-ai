from __future__ import annotations

import pytest

from app.application.submit_command import InvalidCommandError, SubmitCommand, SubmitCommandRequest
from app.domain.status import CommandStatus


def test_submit_command_creates_persists_then_queues(repository, queue, sample_payload) -> None:
    use_case = SubmitCommand(repository, queue)

    result = use_case.execute(SubmitCommandRequest(type="TEST_COMMAND", payload=sample_payload))

    command = repository.get_by_id(result.command_id)
    assert command is not None
    assert command.status == CommandStatus.QUEUED
    assert queue.published == [result.command_id]


def test_submit_command_invalid_envelope_does_not_persist_or_enqueue(repository, queue) -> None:
    use_case = SubmitCommand(repository, queue)

    with pytest.raises(InvalidCommandError):
        use_case.execute(SubmitCommandRequest(type="", payload={}))

    with pytest.raises(InvalidCommandError):
        use_case.execute(SubmitCommandRequest(type="TEST_COMMAND", payload="bad"))  # type: ignore[arg-type]

    assert queue.published == []
