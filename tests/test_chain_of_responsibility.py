from __future__ import annotations

from app.application.pipelines import SequentialCommandPipeline
from app.commands.test_command.handlers import (
    AuditHandler,
    BusinessCommandHandler,
    IdempotencyHandler,
    ValidationHandler,
)
from app.domain.command import Command
from app.domain.context import CommandContext


def test_handlers_execute_in_order() -> None:
    context = CommandContext(Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"}))
    pipeline = SequentialCommandPipeline([ValidationHandler(), IdempotencyHandler(), BusinessCommandHandler(), AuditHandler()])

    pipeline.execute(context)

    assert context.metadata["handler_order"] == [
        "ValidationHandler",
        "IdempotencyHandler",
        "BusinessCommandHandler",
        "AuditHandler",
    ]
    assert context.result == {"echo": "hello"}


def test_invalid_payload_interrupts_before_business_handler() -> None:
    context = CommandContext(Command(id="cmd-1", type="TEST_COMMAND", payload={}))
    pipeline = SequentialCommandPipeline([ValidationHandler(), BusinessCommandHandler(), AuditHandler()])

    pipeline.execute(context)

    assert context.errors == ["TEST_COMMAND payload.message is required"]
    assert context.metadata["handler_order"] == ["ValidationHandler"]
    assert context.result is None


def test_context_metadata_errors_and_result_are_shared() -> None:
    context = CommandContext(Command(id="cmd-1", type="TEST_COMMAND", payload={"message": "hello"}))

    SequentialCommandPipeline([ValidationHandler(), BusinessCommandHandler(), AuditHandler()]).execute(context)

    assert context.errors == []
    assert context.metadata["audited"] is True
    assert context.result == {"echo": "hello"}
