"""Registry for command pipelines.

To add a command type, create a command-specific pipeline module and register it
with HandlerRegistry. The API and worker flows must not change for new types.
"""

from __future__ import annotations

from app.commands.test_command.pipeline import create_test_command_pipeline
from app.domain.ports import CommandPipeline


class PipelineNotFoundError(Exception):
    """Raised when no pipeline has been registered for a command type."""

    pass


class HandlerRegistry:
    """Map command types to pipelines while keeping workers type-agnostic.

    To add a new command type, define its handlers and pipeline, then register
    the pipeline here during composition. The API and worker orchestration stay
    unchanged.
    """

    def __init__(self) -> None:
        """Create an empty command type registry."""
        self._pipelines: dict[str, CommandPipeline] = {}

    def register(self, command_type: str, pipeline: CommandPipeline) -> None:
        """Register the pipeline that handles a normalized command type."""
        normalized = command_type.strip()
        if not normalized:
            raise ValueError("command type is required")
        self._pipelines[normalized] = pipeline

    def get(self, command_type: str) -> CommandPipeline:
        """Return the pipeline for a command type or raise a controlled error."""
        try:
            return self._pipelines[command_type]
        except KeyError as exc:
            raise PipelineNotFoundError(f"No pipeline registered for type {command_type}") from exc


def create_default_registry() -> HandlerRegistry:
    """Create the runtime registry with built-in command pipelines."""
    registry = HandlerRegistry()
    registry.register("TEST_COMMAND", create_test_command_pipeline())
    return registry
