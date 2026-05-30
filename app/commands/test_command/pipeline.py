"""TEST_COMMAND pipeline and extension pattern.

New command types should define their own pipeline factory and register it in
HandlerRegistry composition without changing API or worker orchestration.
"""

from app.application.pipelines import SequentialCommandPipeline
from app.commands.test_command.handlers import (
    AuditHandler,
    BusinessCommandHandler,
    IdempotencyHandler,
    ValidationHandler,
)


def create_test_command_pipeline() -> SequentialCommandPipeline:
    """Build the TEST_COMMAND handler chain in execution order."""
    return SequentialCommandPipeline(
        [
            ValidationHandler(),
            IdempotencyHandler(),
            BusinessCommandHandler(),
            AuditHandler(),
        ]
    )
