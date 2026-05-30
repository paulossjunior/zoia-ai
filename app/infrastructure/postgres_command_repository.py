"""PostgreSQL command repository adapter for durable command persistence."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from app.domain.command import Command
from app.domain.status import CallbackStatus, CommandStatus


class PostgresCommandRepository:
    """Persist command lifecycle snapshots in PostgreSQL."""

    def __init__(self, dsn: str | None = None, connection: Any | None = None) -> None:
        self._external_connection = connection
        if connection is not None:
            self.connection = connection
        else:
            import psycopg

            self.connection = psycopg.connect(dsn or _dsn_from_env(), autocommit=True)
        self.initialize()

    def initialize(self) -> None:
        """Create the commands table and lookup indexes when absent."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS commands (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    payload JSONB NOT NULL,
                    external_id TEXT NULL,
                    callback TEXT NULL,
                    status TEXT NOT NULL,
                    response_payload JSONB NULL,
                    error_message TEXT NULL,
                    callback_status TEXT NOT NULL,
                    callback_error_message TEXT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    request_received_at TIMESTAMPTZ NOT NULL,
                    processing_started_at TIMESTAMPTZ NULL,
                    processing_finished_at TIMESTAMPTZ NULL,
                    callback_sent_at TIMESTAMPTZ NULL
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_commands_external_id_received ON commands (external_id, request_received_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_commands_status_received ON commands (status, request_received_at DESC)")

    def save(self, command: Command) -> None:
        """Insert or replace a command snapshot by id."""
        self._execute_write(command)

    def update(self, command: Command) -> None:
        """Persist the latest command snapshot."""
        self._execute_write(command)

    def get_by_id(self, command_id: str) -> Command | None:
        """Load one command by id."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM commands WHERE id = %s", (command_id,))
            row = cursor.fetchone()
        return _row_to_command(row) if row else None

    def get_latest_by_external_id(self, external_id: str) -> Command | None:
        """Load the newest command for a non-unique external id."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM commands WHERE external_id = %s ORDER BY request_received_at DESC LIMIT 1",
                (external_id,),
            )
            row = cursor.fetchone()
        return _row_to_command(row) if row else None

    def list(
        self,
        status: CommandStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Command], int]:
        """Return a page of commands and total count, optionally filtered."""
        offset = (page - 1) * page_size
        where = "WHERE status = %s" if status else ""
        params: tuple[Any, ...] = (status.value,) if status else ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM commands {where}", params)
            total = int(cursor.fetchone()[0])
            cursor.execute(
                f"SELECT * FROM commands {where} ORDER BY request_received_at DESC LIMIT %s OFFSET %s",
                (*params, page_size, offset),
            )
            rows = cursor.fetchall()
        return [_row_to_command(row) for row in rows], total

    def _execute_write(self, command: Command) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO commands (
                    id, type, payload, external_id, callback, status,
                    response_payload, error_message, callback_status,
                    callback_error_message, retry_count, request_received_at,
                    processing_started_at, processing_finished_at, callback_sent_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    type = EXCLUDED.type,
                    payload = EXCLUDED.payload,
                    external_id = EXCLUDED.external_id,
                    callback = EXCLUDED.callback,
                    status = EXCLUDED.status,
                    response_payload = EXCLUDED.response_payload,
                    error_message = EXCLUDED.error_message,
                    callback_status = EXCLUDED.callback_status,
                    callback_error_message = EXCLUDED.callback_error_message,
                    retry_count = EXCLUDED.retry_count,
                    request_received_at = EXCLUDED.request_received_at,
                    processing_started_at = EXCLUDED.processing_started_at,
                    processing_finished_at = EXCLUDED.processing_finished_at,
                    callback_sent_at = EXCLUDED.callback_sent_at
                """,
                _command_values(command),
            )


def _dsn_from_env() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "zoia")
    user = os.getenv("POSTGRES_USER", "zoia")
    password = os.getenv("POSTGRES_PASSWORD", "zoia")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _command_values(command: Command) -> tuple[Any, ...]:
    return (
        command.id,
        command.type,
        _json_value(command.payload),
        command.external_id,
        command.callback,
        command.status.value,
        _json_value(command.response_payload),
        command.error_message,
        command.callback_status.value,
        command.callback_error_message,
        command.retry_count,
        command.request_received_at,
        command.processing_started_at,
        command.processing_finished_at,
        command.callback_sent_at,
    )


def _row_to_command(row: Any) -> Command:
    data = row if isinstance(row, dict) else _tuple_row_to_dict(row)
    return Command(
        id=data["id"],
        type=data["type"],
        payload=data["payload"],
        external_id=data.get("external_id"),
        callback=data.get("callback"),
        status=CommandStatus(data["status"]),
        response_payload=data.get("response_payload"),
        error_message=data.get("error_message"),
        callback_status=CallbackStatus(data.get("callback_status", "not_required")),
        callback_error_message=data.get("callback_error_message"),
        retry_count=int(data.get("retry_count") or 0),
        created_at=_parse_datetime(data["request_received_at"]),
        started_at=_parse_optional_datetime(data.get("processing_started_at")),
        completed_at=_parse_optional_datetime(data.get("processing_finished_at")),
        callback_sent_at=_parse_optional_datetime(data.get("callback_sent_at")),
    )


def _tuple_row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    columns = [
        "id",
        "type",
        "payload",
        "external_id",
        "callback",
        "status",
        "response_payload",
        "error_message",
        "callback_status",
        "callback_error_message",
        "retry_count",
        "request_received_at",
        "processing_started_at",
        "processing_finished_at",
        "callback_sent_at",
    ]
    return dict(zip(columns, row, strict=True))


def _parse_datetime(value: datetime | str) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def _parse_optional_datetime(value: datetime | str | None) -> datetime | None:
    return None if value is None else _parse_datetime(value)


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        from psycopg.types.json import Jsonb
    except Exception:
        return value
    return Jsonb(value)
