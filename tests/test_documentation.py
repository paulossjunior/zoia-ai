from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.infrastructure.memory_command_repository import MemoryCommandRepository


DOCS_URL = "http://localhost:8000/docs"
OPENAPI_PATH = "/openapi.json"
COMMAND_PATH = "/commands"
COMMAND_DETAIL_PATH = "/commands/{command_id}"
COMMAND_STATUS_PATH = "/commands/{command_id}/status"
COMMAND_EXTERNAL_PATH = "/commands/external/{external_id}"
CANONICAL_COMMAND_REQUEST = {"type": "TEST_COMMAND", "payload": {"message": "hello"}}
ACK_EXAMPLE = {"command_id": "00000000-0000-4000-8000-000000000000", "status": "queued"}
VALIDATION_ERROR_EXAMPLE = {"detail": "invalid command request"}
COMMAND_DETAIL_EXAMPLE = {
    "command_id": "00000000-0000-4000-8000-000000000000",
    "type": "TEST_COMMAND",
    "external_id": None,
    "callback": None,
    "payload": {"message": "hello"},
    "status": "completed",
    "response_payload": {"echo": "hello"},
    "error_message": None,
    "callback_status": "not_required",
    "callback_error_message": None,
    "request_received_at": "2026-05-30T19:00:00Z",
    "processing_started_at": "2026-05-30T19:00:01Z",
    "processing_finished_at": "2026-05-30T19:00:02Z",
    "callback_sent_at": None,
}
COMMAND_STATUS_EXAMPLE = {
    "command_id": "00000000-0000-4000-8000-000000000000",
    "status": "processing",
    "callback_status": "pending",
}
COMMAND_LIST_EXAMPLE = {
    "items": [
        {"id": "1", "type": "SEND_EMAIL", "status": "failed"},
        {"id": "2", "type": "GENERATE_REPORT", "status": "failed"},
    ],
    "total": 2,
    "page": 1,
    "page_size": 20,
}
INVALID_COMMAND_ID_EXAMPLE = {"detail": "invalid command_id"}
COMMAND_NOT_FOUND_EXAMPLE = {"detail": "command not found"}
INVALID_STATUS_EXAMPLE = {"detail": "invalid status"}
INVALID_PAGINATION_EXAMPLE = {"detail": "invalid pagination"}
PUBLIC_DOC_MODULES = [
    Path("app/domain/command.py"),
    Path("app/domain/status.py"),
    Path("app/domain/context.py"),
    Path("app/domain/ports.py"),
    Path("app/domain/handlers.py"),
    Path("app/application/get_command.py"),
    Path("app/application/get_command_by_external_id.py"),
    Path("app/application/submit_command.py"),
    Path("app/application/get_command_status.py"),
    Path("app/application/list_commands.py"),
    Path("app/application/process_command.py"),
    Path("app/application/handler_registry.py"),
    Path("app/application/pipelines.py"),
    Path("app/infrastructure/redis_queue.py"),
    Path("app/infrastructure/redis_command_repository.py"),
    Path("app/infrastructure/postgres_command_repository.py"),
    Path("app/infrastructure/http_callback_client.py"),
    Path("app/infrastructure/memory_command_repository.py"),
    Path("app/infrastructure/logging.py"),
    Path("app/api/main.py"),
    Path("app/api/schemas.py"),
    Path("app/api/routes.py"),
    Path("app/worker/main.py"),
    Path("app/commands/test_command/handlers.py"),
    Path("app/commands/test_command/pipeline.py"),
]
PUBLIC_DOC_TARGETS = {
    Path("app/domain/command.py"): ["Command", "utcnow", "safe_error_message"],
    Path("app/domain/status.py"): ["CommandStatus", "CallbackStatus"],
    Path("app/domain/context.py"): ["CommandContext"],
    Path("app/domain/ports.py"): ["CommandRepository", "CommandQueue", "CommandHandler", "CommandPipeline"],
    Path("app/domain/handlers.py"): ["BaseCommandHandler", "RecordingHandler"],
    Path("app/application/get_command.py"): [
        "GetCommand",
        "GetCommandRequest",
        "GetCommandResult",
        "InvalidCommandIdError",
        "CommandNotFoundError",
    ],
    Path("app/application/submit_command.py"): ["SubmitCommand", "SubmitCommandRequest", "SubmitCommandResult", "InvalidCommandError"],
    Path("app/application/get_command_status.py"): [
        "GetCommandStatus",
        "GetCommandStatusRequest",
        "GetCommandStatusResult",
        "CommandStatusNotFoundError",
    ],
    Path("app/application/get_command_by_external_id.py"): [
        "GetCommandByExternalId",
        "GetCommandByExternalIdRequest",
        "InvalidExternalIdError",
    ],
    Path("app/application/list_commands.py"): [
        "ListCommands",
        "ListCommandsRequest",
        "ListCommandsResult",
        "CommandSummary",
        "InvalidCommandStatusError",
        "InvalidPaginationError",
    ],
    Path("app/application/process_command.py"): [
        "ProcessCommand",
        "ProcessCommandRequest",
        "ProcessCommandResult",
        "CommandNotFoundError",
    ],
    Path("app/application/handler_registry.py"): ["HandlerRegistry", "PipelineNotFoundError", "create_default_registry"],
    Path("app/application/pipelines.py"): ["SequentialCommandPipeline"],
    Path("app/infrastructure/redis_queue.py"): ["RedisCommandQueue"],
    Path("app/infrastructure/redis_command_repository.py"): ["RedisCommandRepository"],
    Path("app/infrastructure/postgres_command_repository.py"): ["PostgresCommandRepository"],
    Path("app/infrastructure/http_callback_client.py"): ["HttpCallbackClient"],
    Path("app/infrastructure/memory_command_repository.py"): ["MemoryCommandRepository"],
    Path("app/infrastructure/logging.py"): ["configure_logging"],
    Path("app/api/main.py"): ["create_app"],
    Path("app/api/schemas.py"): [
        "SubmitCommandRequest",
        "SubmitCommandResponse",
        "CommandDetailResponse",
        "CommandStatusResponse",
        "CommandSummaryResponse",
        "CommandListResponse",
        "ErrorResponse",
    ],
    Path("app/api/routes.py"): ["submit_command", "list_commands", "get_command_by_external_id", "get_command_status_only", "get_command"],
    Path("app/worker/main.py"): ["create_worker_dependencies", "process_one", "run_forever", "main"],
    Path("app/commands/test_command/handlers.py"): [
        "ValidationHandler",
        "IdempotencyHandler",
        "BusinessCommandHandler",
        "AuditHandler",
    ],
    Path("app/commands/test_command/pipeline.py"): ["create_test_command_pipeline"],
}
EXTERNAL_API_FORBIDDEN_TERMS = ("redis", "rpush", "blpop", "repository", "broker")
DOMAIN_FORBIDDEN_IMPORT_PREFIXES = ("fastapi", "redis", "docker", "app.infrastructure")


class DocumentationQueue:
    def __init__(self) -> None:
        self.published: list[str] = []

    def publish(self, command_id: str) -> None:
        self.published.append(command_id)

    def consume(self, timeout: int = 0) -> str | None:
        return None


def _client() -> TestClient:
    return TestClient(create_app(MemoryCommandRepository(), DocumentationQueue()))


def _openapi() -> dict[str, Any]:
    return _client().get(OPENAPI_PATH).json()


def _commands_operation() -> dict[str, Any]:
    return _openapi()["paths"][COMMAND_PATH]["post"]


def _command_list_operation() -> dict[str, Any]:
    return _openapi()["paths"][COMMAND_PATH]["get"]


def _command_detail_operation() -> dict[str, Any]:
    return _openapi()["paths"][COMMAND_DETAIL_PATH]["get"]


def _command_status_operation() -> dict[str, Any]:
    return _openapi()["paths"][COMMAND_STATUS_PATH]["get"]


def _command_external_operation() -> dict[str, Any]:
    return _openapi()["paths"][COMMAND_EXTERNAL_PATH]["get"]


def _schema(name: str) -> dict[str, Any]:
    return _openapi()["components"]["schemas"][name]


def _walk_examples(value: Any) -> list[Any]:
    examples: list[Any] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in {"example", "examples"}:
                examples.append(nested)
            examples.extend(_walk_examples(nested))
            if isinstance(nested, dict) and "value" in nested:
                examples.append(nested["value"])
    elif isinstance(value, list):
        for nested in value:
            examples.extend(_walk_examples(nested))
    return examples


def test_docs_page_is_reachable() -> None:
    response = _client().get("/docs")

    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_openapi_documents_post_commands_operation() -> None:
    operation = _commands_operation()

    assert operation["summary"] == "Submit command"
    assert "asynchronous processing" in operation["description"]
    assert operation["tags"] == ["commands"]


def test_command_request_schema_documents_required_fields() -> None:
    schema = _schema("SubmitCommandRequest")

    assert set(schema["required"]) == {"type", "payload"}
    assert schema["properties"]["type"]["description"]
    assert schema["properties"]["payload"]["description"]


def test_command_acknowledgement_response_is_documented() -> None:
    operation = _commands_operation()
    response = operation["responses"]["202"]

    assert "accepted" in response["description"].lower()
    assert _schema("SubmitCommandResponse")["properties"].keys() >= {"command_id", "status"}
    assert ACK_EXAMPLE in _walk_examples(response)


def test_command_validation_error_response_is_documented() -> None:
    operation = _commands_operation()
    response = operation["responses"]["400"]

    assert "invalid" in response["description"].lower()
    assert VALIDATION_ERROR_EXAMPLE in _walk_examples(response)


def test_documented_test_command_example_matches_endpoint_behavior() -> None:
    operation = _commands_operation()

    assert CANONICAL_COMMAND_REQUEST in _walk_examples(operation)
    response = _client().post(COMMAND_PATH, json=CANONICAL_COMMAND_REQUEST)

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert response.json()["command_id"]


def test_public_openapi_does_not_require_queue_implementation_details() -> None:
    operation_text = json.dumps([_commands_operation(), _command_detail_operation(), _command_status_operation(), _command_list_operation()]).lower()

    for term in EXTERNAL_API_FORBIDDEN_TERMS:
        assert term not in operation_text


def test_required_command_processing_modules_have_module_docstrings() -> None:
    for path in PUBLIC_DOC_MODULES:
        tree = ast.parse(path.read_text())
        assert ast.get_docstring(tree), f"{path} is missing a module docstring"


def test_domain_modules_do_not_import_infrastructure_or_frameworks() -> None:
    for path in Path("app/domain").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names = [node.module]
            else:
                continue
            for imported_name in imported_names:
                assert not imported_name.startswith(DOMAIN_FORBIDDEN_IMPORT_PREFIXES), f"{path} imports {imported_name}"


def test_public_command_processing_targets_have_docstrings() -> None:
    for path, target_names in PUBLIC_DOC_TARGETS.items():
        tree = ast.parse(path.read_text())
        nodes = {node.name: node for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
        for target_name in target_names:
            assert target_name in nodes, f"{path} no longer defines {target_name}"
            assert ast.get_docstring(nodes[target_name]), f"{path}:{target_name} is missing a docstring"


def test_registry_and_pipeline_document_command_type_extension() -> None:
    registry_text = Path("app/application/handler_registry.py").read_text().lower()
    pipeline_text = Path("app/commands/test_command/pipeline.py").read_text().lower()

    assert "new command type" in registry_text
    assert "register" in registry_text
    assert "worker" in registry_text
    assert "new command types" in pipeline_text
    assert "worker" in pipeline_text


def test_readme_documents_local_api_docs_url() -> None:
    assert DOCS_URL in Path("README.md").read_text()


def test_readme_command_example_matches_openapi_example() -> None:
    readme = Path("README.md").read_text()
    operation = _commands_operation()

    assert json.dumps(CANONICAL_COMMAND_REQUEST, separators=(",", ":")) in readme
    assert CANONICAL_COMMAND_REQUEST in _walk_examples(operation)


def test_readme_documents_new_command_type_guidance() -> None:
    readme = Path("README.md").read_text().lower()

    for word in ("pipeline", "handlers", "registry", "payload contract"):
        assert word in readme


def test_readme_says_external_clients_do_not_need_queue_details() -> None:
    readme = Path("README.md").read_text().lower()

    assert "external clients do not need" in readme
    assert "queue implementation" in readme


def test_openapi_documents_get_command_detail_operation() -> None:
    operation = _command_detail_operation()

    assert operation["summary"] == "Get command record"
    assert "read-only" in operation["description"]
    assert "complete persisted execution record" in operation["description"]
    assert operation["tags"] == ["commands"]


def test_openapi_command_detail_schema_includes_complete_record_fields() -> None:
    schema = _schema("CommandDetailResponse")

    assert set(schema["required"]) == {"command_id", "type", "payload", "status", "callback_status", "request_received_at"}
    assert schema["properties"].keys() >= {
        "command_id",
        "type",
        "external_id",
        "callback",
        "payload",
        "status",
        "response_payload",
        "error_message",
        "callback_status",
        "callback_error_message",
        "request_received_at",
        "processing_started_at",
        "processing_finished_at",
        "callback_sent_at",
    }
    examples = _walk_examples(_command_detail_operation())
    assert any(
        isinstance(example, dict)
        and example.items() <= COMMAND_DETAIL_EXAMPLE.items()
        and example.get("command_id") == COMMAND_DETAIL_EXAMPLE["command_id"]
        for example in examples
    )


def test_openapi_command_status_schema_is_status_only() -> None:
    schema = _schema("CommandStatusResponse")

    assert set(schema["required"]) == {"command_id", "status", "callback_status"}
    assert set(schema["properties"]) == {"command_id", "status", "callback_status"}
    assert COMMAND_STATUS_EXAMPLE in _walk_examples(_command_status_operation())


def test_openapi_documents_external_id_lookup_operation() -> None:
    operation = _command_external_operation()

    assert operation["summary"] == "Get latest command by external id"
    assert operation["tags"] == ["commands"]
    assert "external id" in operation["description"].lower()


def test_openapi_command_list_schema_includes_summaries_and_pagination() -> None:
    schema = _schema("CommandListResponse")
    operation = _command_list_operation()

    assert set(schema["required"]) == {"items", "total", "page", "page_size"}
    parameters = {parameter["name"] for parameter in operation["parameters"]}
    assert parameters >= {"status", "page", "page_size"}
    assert COMMAND_LIST_EXAMPLE in _walk_examples(operation)


def test_openapi_documents_invalid_command_id_response() -> None:
    response = _command_detail_operation()["responses"]["400"]

    assert "invalid" in response["description"].lower()
    assert INVALID_COMMAND_ID_EXAMPLE in _walk_examples(response)


def test_openapi_documents_command_not_found_response() -> None:
    response = _command_detail_operation()["responses"]["404"]

    assert "not found" in response["description"].lower()
    assert COMMAND_NOT_FOUND_EXAMPLE in _walk_examples(response)


def test_readme_documents_command_status_query() -> None:
    readme = Path("README.md").read_text()
    lowered = readme.lower()

    assert "GET /commands/{command_id}" in readme
    assert "GET /commands/{command_id}/status" in readme
    assert "GET /commands?status=failed&page=1&page_size=20" in readme
    assert "curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000" in readme
    assert '"payload"' in readme
    assert '"response_payload"' in readme
    assert '"request_received_at"' in readme
    assert '"processing_started_at"' in readme
    assert '"processing_finished_at"' in readme
    assert "invalid command_id" in readme
    assert "command not found" in readme
    assert "read-only" in lowered


def test_openapi_documents_list_query_errors() -> None:
    response = _command_list_operation()["responses"]["400"]

    assert "invalid" in response["description"].lower()
    examples = _walk_examples(response)
    assert INVALID_STATUS_EXAMPLE in examples
    assert INVALID_PAGINATION_EXAMPLE in examples


def test_persisted_command_record_contract_examples_are_documented() -> None:
    readme = Path("README.md").read_text()

    for status in ('"queued"', '"completed"', '"failed"'):
        assert status in readme
    for field in (
        "command_id",
        "payload",
        "response_payload",
        "error_message",
        "request_received_at",
        "processing_started_at",
        "processing_finished_at",
    ):
        assert f'"{field}"' in readme
