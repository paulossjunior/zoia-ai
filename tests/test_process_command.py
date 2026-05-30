from __future__ import annotations

from app.application.handler_registry import HandlerRegistry
from app.application.pipelines import SequentialCommandPipeline
from app.application.process_command import ProcessCommand, ProcessCommandRequest
from app.domain.command import Command
from app.domain.status import CommandStatus
from tests.conftest import FakeHandler


def test_process_command_known_type_transitions_to_completed(repository, fake_pipeline) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"})
    repository.save(command)
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", fake_pipeline)

    result = ProcessCommand(repository, registry).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.COMPLETED
    assert saved.status == CommandStatus.COMPLETED
    assert saved.started_at is not None
    assert saved.completed_at is not None


def test_process_command_unknown_type_marks_failed(repository) -> None:
    command = Command(id="cmd-1", type="UNKNOWN", payload={"message": "hello"})
    repository.save(command)

    result = ProcessCommand(repository, HandlerRegistry()).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.FAILED
    assert saved.error_message == "No pipeline registered for type UNKNOWN"
    assert saved.completed_at is not None


def test_process_command_handler_exception_marks_failed(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"})
    repository.save(command)
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", SequentialCommandPipeline([FakeHandler("bad", raise_error=True)]))

    result = ProcessCommand(repository, registry).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.FAILED
    assert "Handler execution failed" in saved.error_message
    assert saved.completed_at is not None


def test_registering_new_type_executes_without_worker_changes(repository) -> None:
    command = Command(id="cmd-2", type="NEW_COMMAND", payload={"message": "hello"})
    repository.save(command)
    registry = HandlerRegistry()
    registry.register("NEW_COMMAND", SequentialCommandPipeline([FakeHandler("new")]))

    result = ProcessCommand(repository, registry).execute(ProcessCommandRequest(command_id="cmd-2"))

    assert result.status == CommandStatus.COMPLETED
