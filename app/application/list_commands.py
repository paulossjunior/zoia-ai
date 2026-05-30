"""Read-only use case for listing commands by status with pagination."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.ports import CommandRepository
from app.domain.status import CommandStatus


class InvalidCommandStatusError(ValueError):
    """Raised when a list query receives an unsupported status filter."""

    pass


class InvalidPaginationError(ValueError):
    """Raised when a list query receives invalid pagination values."""

    pass


@dataclass(frozen=True)
class ListCommandsRequest:
    """Input contract for listing command summaries."""

    status: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class CommandSummary:
    """Compact command view used in list responses."""

    id: str
    type: str
    status: CommandStatus


@dataclass(frozen=True)
class ListCommandsResult:
    """Paginated command list returned to external clients."""

    items: list[CommandSummary]
    total: int
    page: int
    page_size: int


class ListCommands:
    """List command summaries without mutating state or processing work."""

    def __init__(self, repository: CommandRepository) -> None:
        """Create the use case with the command repository port."""
        self.repository = repository

    def execute(self, request: ListCommandsRequest) -> ListCommandsResult:
        """Validate filters, load a page, and map commands to summaries."""
        status = _parse_status(request.status)
        page, page_size = _validate_pagination(request.page, request.page_size)
        commands, total = self.repository.list(status=status, page=page, page_size=page_size)
        return ListCommandsResult(
            items=[
                CommandSummary(id=command.id, type=command.type, status=command.status)
                for command in commands
            ],
            total=total,
            page=page,
            page_size=page_size,
        )


def _parse_status(status: str | None) -> CommandStatus | None:
    """Parse an optional status filter into a command status enum."""
    if status is None:
        return None
    try:
        return CommandStatus(str(status))
    except ValueError as exc:
        raise InvalidCommandStatusError("invalid status") from exc


def _validate_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Validate page and page size values."""
    if page < 1 or page_size < 1:
        raise InvalidPaginationError("invalid pagination")
    return page, page_size
