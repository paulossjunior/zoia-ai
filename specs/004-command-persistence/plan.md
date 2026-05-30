# Implementation Plan: Command Persistence

**Branch**: `004-command-persistence` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-command-persistence/spec.md`

## Summary

Extend the command model and persistence contract so every accepted command keeps a complete execution record: original payload, current status, processing response, error message, request receipt time, processing start time, and processing finish time. The implementation will update the domain entity and repository adapters through existing ports, persist handler results and failures during worker processing, and expose a complete command retrieval contract while preserving the current status lookup behavior.

## Technical Context

**Language/Version**: Python 3.12 target runtime; current local tests may execute with the active virtualenv interpreter  
**Primary Dependencies**: Existing FastAPI, Pydantic, Redis adapter, Docker Compose, RedisInsight, and pytest stack; no new runtime dependency required  
**Storage**: Existing command repository abstraction with Redis-backed runtime storage and in-memory test storage  
**Testing**: Pytest with use case tests, FastAPI TestClient tests, repository adapter tests or fakes, worker processing tests, and documentation checks  
**Target Platform**: Existing Docker Compose local environment with API, worker, Redis, and RedisInsight  
**Project Type**: Web service plus worker  
**Performance Goals**: Command persistence and status updates should remain lightweight enough that HTTP submission still returns immediately after validation, persistence, and queue publication  
**Constraints**: Domain must remain framework/storage independent; command must be persisted before queue publication; payload must survive all status updates; response/error/timestamps must be persisted through success and failure; Redis remains an adapter detail  
**Scale/Scope**: Covers command entity fields, lifecycle methods, repository serialization, submit/process use cases, command status/full retrieval schemas, worker outcome persistence, tests, and README/OpenAPI documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. Command fields and lifecycle behavior live in `app/domain`; storage mechanics remain in infrastructure adapters.
- **Asynchronous command flow**: PASS. HTTP submission still validates, persists, enqueues, and returns. Worker processing still owns business execution and outcome updates.
- **Explicit contracts**: PASS. The feature defines persisted record fields, lifecycle timestamps, response/error fields, retrieval response shape, and allowed states.
- **Infrastructure abstraction**: PASS. Command persistence continues through `CommandRepository`; Redis and in-memory implementations remain adapters behind the port.
- **Observability**: PASS. Status, timestamps, response, and error data are persisted for submission, processing start, completion, and failure. Logs remain required for these lifecycle events.
- **Testing discipline**: PASS. Tests will cover persistence-before-queueing, payload retention, success response persistence, failure error persistence, repository serialization, retrieval, and proof that API submission does not execute processing.
- **Handler extensibility**: PASS. No new command type is introduced. Pipelines remain registered through the existing handler registry; handler results are captured generically from command context.

Post-design re-check: PASS. Research, data model, contracts, and quickstart preserve layered architecture, asynchronous processing, explicit persistence contracts, and storage replaceability.

## Project Structure

### Documentation (this feature)

```text
specs/004-command-persistence/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── command-persistence-contract.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py       # Add response and lifecycle timestamp aliases/fields
│   ├── context.py       # Reuse handler result for command response persistence
│   └── status.py        # Reuse explicit lifecycle states
├── application/
│   ├── submit_command.py
│   ├── process_command.py
│   └── get_command_status.py
├── infrastructure/
│   ├── redis_command_repository.py
│   └── memory_command_repository.py
├── api/
│   ├── schemas.py       # Add complete execution record response
│   └── routes.py        # Expose/reuse command retrieval contract
└── commands/
    └── test_command/
        └── handlers.py  # Existing result source for success response

tests/
├── test_submit_command.py
├── test_process_command.py
├── test_get_command_status.py
├── test_api.py
├── test_documentation.py
└── test_worker.py

README.md
```

**Structure Decision**: Update existing layered modules in place. The core change is widening the existing command record and repository serialization rather than introducing a separate persistence subsystem.

## Complexity Tracking

No constitution violations or additional complexity are planned.
