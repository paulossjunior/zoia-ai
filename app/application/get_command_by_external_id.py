"""Read-only use case for retrieving the latest command by external id."""

from __future__ import annotations

from dataclasses import dataclass

from app.application.get_command import CommandNotFoundError, GetCommandResult
from app.domain.ports import CommandRepository


class InvalidExternalIdError(ValueError):
    """Raised when external id lookup receives a blank identifier."""

    pass


@dataclass(frozen=True)
class GetCommandByExternalIdRequest:
    """Input contract for reading the latest command by external id."""

    external_id: str


class GetCommandByExternalId:
    """Fetch the most recent command associated with an external business id."""

    def __init__(self, repository: CommandRepository) -> None:
        self.repository = repository

    def execute(self, request: GetCommandByExternalIdRequest) -> GetCommandResult:
        external_id = request.external_id.strip() if isinstance(request.external_id, str) else ""
        if not external_id:
            raise InvalidExternalIdError("invalid external_id")
        command = self.repository.get_latest_by_external_id(external_id)
        if command is None:
            raise CommandNotFoundError("command not found")
        return GetCommandResult(
            command_id=command.id,
            type=command.type,
            status=command.status,
            payload=command.payload,
            external_id=command.external_id,
            callback=command.callback,
            response_payload=command.response_payload,
            error_message=command.error_message,
            callback_status=command.callback_status,
            callback_error_message=command.callback_error_message,
            request_received_at=command.request_received_at,
            processing_started_at=command.processing_started_at,
            processing_finished_at=command.processing_finished_at,
            callback_sent_at=command.callback_sent_at,
        )
