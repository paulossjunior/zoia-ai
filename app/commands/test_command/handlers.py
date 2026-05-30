"""Handlers that implement the TEST_COMMAND processing chain."""

from __future__ import annotations

from app.domain.context import CommandContext
from app.domain.handlers import BaseCommandHandler


class ValidationHandler(BaseCommandHandler):
    """Validate the TEST_COMMAND payload contract before business execution."""

    def handle(self, context: CommandContext) -> None:
        """Require a non-blank payload.message value."""
        context.metadata.setdefault("handler_order", []).append("ValidationHandler")
        message = context.command.payload.get("message")
        if not isinstance(message, str) or not message.strip():
            context.add_error("TEST_COMMAND payload.message is required")


class IdempotencyHandler(BaseCommandHandler):
    """Prevent duplicate processing within the current pipeline context."""

    def handle(self, context: CommandContext) -> None:
        """Record the command id and interrupt when it was already processed."""
        context.metadata.setdefault("handler_order", []).append("IdempotencyHandler")
        processed = context.metadata.setdefault("processed_command_ids", set())
        if context.command.id in processed:
            context.add_error("Command already processed")
            return
        processed.add(context.command.id)


class BusinessCommandHandler(BaseCommandHandler):
    """Execute the primary TEST_COMMAND behavior after validation passes."""

    def handle(self, context: CommandContext) -> None:
        """Echo the validated message into the shared command result."""
        context.metadata.setdefault("handler_order", []).append("BusinessCommandHandler")
        context.result = {"echo": context.command.payload["message"]}


class AuditHandler(BaseCommandHandler):
    """Record that TEST_COMMAND processing reached the audit step."""

    def handle(self, context: CommandContext) -> None:
        """Mark the shared context as audited."""
        context.metadata.setdefault("handler_order", []).append("AuditHandler")
        context.metadata["audited"] = True
