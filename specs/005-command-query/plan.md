# Implementation Plan: Command Query

**Branch**: `005-command-query` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-command-query/spec.md`

## Summary

Add query capabilities for previously submitted commands: full command details by id, lightweight status-only lookup by id, and paginated listing filtered by status. The implementation will extend the existing command repository port with query/list operations, keep Redis and in-memory storage behind adapters, add application use cases for query flows, and expose explicit FastAPI/Pydantic response contracts without changing the asynchronous submission or worker processing flow.

## Technical Context

**Language/Version**: Python 3.12 target runtime; current local virtualenv may run a newer Python interpreter  
**Primary Dependencies**: Existing FastAPI, Pydantic, Redis adapter, Docker Compose, RedisInsight, and pytest stack; no new runtime dependency required  
**Storage**: Existing `CommandRepository` abstraction with Redis-backed runtime storage and in-memory test storage  
**Testing**: Pytest with application use case tests, FastAPI TestClient tests, repository adapter/fake coverage, documentation checks, and architecture checks  
**Target Platform**: Existing Docker Compose local environment with API, worker, Redis, and RedisInsight  
**Project Type**: Web service plus asynchronous worker  
**Performance Goals**: Detail and status lookups should remain lightweight for single-command polling; command list queries must return bounded paginated responses rather than unbounded records  
**Constraints**: Domain remains framework/storage independent; command query flows must not enqueue or process work; Redis remains an adapter detail; list items must omit payload/response details; status-only response must include only id and status  
**Scale/Scope**: Covers repository query/list contract, application query use cases, API schemas/routes, Redis/in-memory adapters, tests, README/OpenAPI documentation, and quickstart examples

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. Query contracts are exposed through domain/application ports and application use cases. FastAPI and Redis remain outside the domain layer.
- **Asynchronous command flow**: PASS. This feature is read-only for existing commands. It does not alter submission, queueing, worker execution, or handler pipelines.
- **Explicit contracts**: PASS. Contracts are required for full detail lookup, status-only lookup, list-by-status, pagination metadata, validation errors, not-found errors, and allowed status values.
- **Infrastructure abstraction**: PASS. Query/list behavior will be added to `CommandRepository`; Redis and in-memory implementations remain adapters behind the port.
- **Observability**: PASS. Query operations should log lookup success, not-found, invalid id, invalid status, and list filter/page metadata without logging full payloads.
- **Testing discipline**: PASS. Tests must cover successful detail lookup, status-only lookup, list filtering, pagination, invalid ids, missing commands, invalid statuses, and proof that query APIs do not enqueue or execute handlers.
- **Handler extensibility**: PASS. Query flows are command-type agnostic and do not change handler registration or pipeline execution.

Post-design re-check: PASS. Research, data model, contracts, and quickstart preserve layered architecture, explicit contracts, infrastructure replaceability, read-only query behavior, and required test coverage.

## Project Structure

### Documentation (this feature)

```text
specs/005-command-query/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── command-query-contract.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py
│   ├── status.py
│   └── ports.py                  # Extend CommandRepository query/list contract
├── application/
│   ├── get_command.py            # Full command detail lookup
│   ├── get_command_status.py     # Status-only lookup contract
│   └── list_commands.py          # Paginated status-filtered listing
├── infrastructure/
│   ├── redis_command_repository.py
│   └── memory_command_repository.py
└── api/
    ├── schemas.py
    └── routes.py

tests/
├── test_api.py
├── test_get_command.py
├── test_get_command_status.py
├── test_list_commands.py
├── test_documentation.py
└── test_architecture.py

README.md
```

**Structure Decision**: Update the existing layered service in place. This feature adds read-only query use cases and repository capabilities; it does not introduce a new service or change worker orchestration.

## Complexity Tracking

No constitution violations or additional complexity are planned.
