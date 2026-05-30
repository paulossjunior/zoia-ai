from __future__ import annotations

from app.domain.command import Command
from app.domain.status import CallbackStatus, CommandStatus
from app.infrastructure.postgres_command_repository import PostgresCommandRepository


class FakeCursor:
    def __init__(self, connection) -> None:
        self.connection = connection
        self._fetchone = None
        self._fetchall = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def execute(self, sql: str, params: tuple | None = None) -> None:
        self.connection.statements.append((sql, params))
        normalized = " ".join(sql.lower().split())
        if normalized.startswith("select * from commands where id"):
            self._fetchone = self.connection.row
        elif normalized.startswith("select * from commands where external_id"):
            self._fetchone = self.connection.row
        elif normalized.startswith("select count(*)"):
            self._fetchone = (1,)
        elif normalized.startswith("select * from commands"):
            self._fetchall = [self.connection.row] if self.connection.row else []

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return self._fetchall


class FakeConnection:
    def __init__(self) -> None:
        self.statements = []
        self.row = None

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)


def test_postgres_repository_inserts_and_reads_command_snapshot() -> None:
    connection = FakeConnection()
    command = Command(
        id="cmd-1",
        type="TEST_COMMAND",
        payload={"message": "hello"},
        external_id="EXT-1",
        callback="https://callback",
    )
    command.mark_processing()
    command.mark_completed({"ok": True})
    command.mark_callback_sent()
    connection.row = (
        command.id,
        command.type,
        command.payload,
        command.external_id,
        command.callback,
        command.status.value,
        command.response_payload,
        command.error_message,
        command.callback_status.value,
        command.callback_error_message,
        command.retry_count,
        command.request_received_at,
        command.processing_started_at,
        command.processing_finished_at,
        command.callback_sent_at,
    )

    repository = PostgresCommandRepository(connection=connection)
    repository.save(command)
    loaded = repository.get_by_id("cmd-1")

    assert any("insert into commands" in sql.lower() for sql, _params in connection.statements)
    assert loaded.id == "cmd-1"
    assert loaded.external_id == "EXT-1"
    assert loaded.callback_status == CallbackStatus.SENT
    assert loaded.response_payload == {"ok": True}


def test_postgres_repository_latest_by_external_id_and_list_use_expected_queries() -> None:
    connection = FakeConnection()
    command = Command(id="cmd-1", type="TEST_COMMAND", payload={}, external_id="EXT-1")
    connection.row = (
        command.id,
        command.type,
        command.payload,
        command.external_id,
        command.callback,
        command.status.value,
        command.response_payload,
        command.error_message,
        command.callback_status.value,
        command.callback_error_message,
        command.retry_count,
        command.request_received_at,
        command.processing_started_at,
        command.processing_finished_at,
        command.callback_sent_at,
    )
    repository = PostgresCommandRepository(connection=connection)

    latest = repository.get_latest_by_external_id("EXT-1")
    items, total = repository.list(status=CommandStatus.QUEUED)

    assert latest.id == "cmd-1"
    assert total == 1
    assert items[0].id == "cmd-1"
    assert any("external_id" in sql.lower() and "order by request_received_at desc" in sql.lower() for sql, _ in connection.statements)
