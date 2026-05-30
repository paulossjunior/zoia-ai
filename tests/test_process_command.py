from __future__ import annotations

from app.application.handler_registry import HandlerRegistry
from app.application.pipelines import SequentialCommandPipeline
from app.application.process_command import ProcessCommand, ProcessCommandRequest
from app.domain.command import Command
from app.domain.status import CommandStatus
from tests.conftest import FakeHandler


class RecordingPipeline:
    def __init__(self, repository) -> None:
        self.repository = repository

    def execute(self, context):
        saved = self.repository.get_by_id(context.command.id)
        assert saved.status == CommandStatus.PROCESSING
        assert saved.processing_started_at is not None
        context.result = {"recorded": True}
        return context


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
    assert saved.response == {"handler": "fake"}
    assert saved.error_message is None
    assert saved.payload == {"message": "hello"}


def test_process_command_unknown_type_marks_failed(repository) -> None:
    command = Command(id="cmd-1", type="UNKNOWN", payload={"message": "hello"})
    repository.save(command)

    result = ProcessCommand(repository, HandlerRegistry()).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.FAILED
    assert saved.error_message == "No pipeline registered for type UNKNOWN"
    assert saved.completed_at is not None
    assert saved.response is None
    assert saved.payload == {"message": "hello"}


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
    assert saved.response is None
    assert saved.payload == {"message": "hello"}


def test_process_command_persists_processing_before_pipeline_execution(repository) -> None:
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"})
    repository.save(command)
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", RecordingPipeline(repository))

    result = ProcessCommand(repository, registry).execute(ProcessCommandRequest(command_id="cmd-1"))

    saved = repository.get_by_id("cmd-1")
    assert result.status == CommandStatus.COMPLETED
    assert saved.response == {"recorded": True}
    assert saved.processing_finished_at is not None


def test_registering_new_type_executes_without_worker_changes(repository) -> None:
    command = Command(id="cmd-2", type="NEW_COMMAND", payload={"message": "hello"})
    repository.save(command)
    registry = HandlerRegistry()
    registry.register("NEW_COMMAND", SequentialCommandPipeline([FakeHandler("new")]))

    result = ProcessCommand(repository, registry).execute(ProcessCommandRequest(command_id="cmd-2"))

    assert result.status == CommandStatus.COMPLETED
