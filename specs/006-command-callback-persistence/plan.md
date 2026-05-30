# Implementation Plan: Command Callback Persistence

**Branch**: `006-command-callback-persistence` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-command-callback-persistence/spec.md`

## Summary

Extend the asynchronous command service so submissions can include optional `external_id` and optional `callback`, commands are durably persisted in PostgreSQL before Redis queue publication, workers persist processing outcomes, optional callbacks are delivered after final success or failure, and clients can query commands by command id, status, or the most recent matching external id. The domain remains technology-free; PostgreSQL, Redis, and HTTP callback delivery are infrastructure adapters behind application ports.

## Technical Context

**Language/Version**: Python 3.12 target runtime; current local virtualenv may run a newer Python interpreter  
**Primary Dependencies**: Existing FastAPI, Pydantic, Redis, Docker Compose, RedisInsight, and pytest stack; add PostgreSQL driver and HTTP client dependencies behind infrastructure adapters  
**Storage**: PostgreSQL for command persistence and audit fields; Redis only for queueing command ids; in-memory repository remains for unit tests  
**Testing**: Pytest with application use case tests, FastAPI TestClient tests, repository adapter tests/fakes, callback client fakes, worker tests, documentation checks, and architecture checks  
**Target Platform**: Docker Compose local environment with API, worker, Redis, RedisInsight, and PostgreSQL  
**Project Type**: Web service plus asynchronous worker  
**Performance Goals**: HTTP submission returns immediately after validation, persistence, and queue publication; callback delivery happens after processing and must not block the original submission request  
**Constraints**: Domain must not import FastAPI, Redis, PostgreSQL, Docker, or HTTP clients; API must not execute command business logic; Redis is queue-only; PostgreSQL is persistence-only; callback failures do not alter processing status; command records are retained after completion or failure  
**Scale/Scope**: Covers command entity fields, callback status lifecycle, PostgreSQL adapter, Redis queue usage, submit/process/query use cases, callback delivery adapter, API contracts, worker orchestration, Docker Compose, tests, README, and ADR updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. Command state, callback status, and lifecycle rules live in `app/domain`; FastAPI, Redis, PostgreSQL, and HTTP delivery stay in infrastructure adapters.
- **Asynchronous command flow**: PASS. `POST /commands` validates, persists, queues, and returns. Worker processing owns pipeline execution and post-processing callback delivery.
- **Explicit contracts**: PASS. Contracts are defined for submission, command detail, status lookup, external id lookup, callback payloads, validation errors, not-found errors, processing states, and callback states.
- **Infrastructure abstraction**: PASS. Persistence uses `CommandRepository`; queueing uses `CommandQueue`; callback delivery will use a new application port such as `CallbackClient`.
- **Observability**: PASS. Submission, processing start, processing success/failure, callback attempt, callback success, and callback failure must be logged and reflected in persisted status fields.
- **Testing discipline**: PASS. Tests must cover valid/invalid submission, persistence before queue, success/failure processing, callback sent/not-required/failed, query by command id/status/external id, queue adapter/fakes, and proof API submission does not process handlers directly.
- **Handler extensibility**: PASS. Command pipelines remain resolved through `HandlerRegistry`; adding new command types still requires a new pipeline/handlers and registration, not worker flow changes.

Post-design re-check: PASS. Research, data model, contracts, and quickstart preserve layered architecture, asynchronous processing, infrastructure replaceability, explicit contracts, observability, and handler extensibility.

## Project Structure

### Documentation (this feature)

```text
specs/006-command-callback-persistence/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── command-api-contract.md
│   └── callback-contract.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py              # Add external_id, callback, response_payload, callback fields
│   ├── status.py               # Add callback status enum
│   └── ports.py                # Add CallbackClient and external-id repository queries
├── application/
│   ├── submit_command.py
│   ├── process_command.py
│   ├── get_command.py
│   ├── get_command_status.py
│   └── get_command_by_external_id.py
├── infrastructure/
│   ├── postgres_command_repository.py
│   ├── redis_queue.py
│   ├── http_callback_client.py
│   └── memory_command_repository.py
├── api/
│   ├── schemas.py
│   ├── routes.py
│   └── main.py
└── worker/
    └── main.py

tests/
├── test_api.py
├── test_submit_command.py
├── test_process_command.py
├── test_callback_delivery.py
├── test_get_command.py
├── test_get_command_status.py
├── test_get_command_by_external_id.py
├── test_postgres_command_repository.py
├── test_documentation.py
└── test_architecture.py

docker-compose.yml
pyproject.toml
README.md
docs/adr/
```

**Structure Decision**: Update the existing layered service in place. Add PostgreSQL and callback delivery as infrastructure adapters, keep Redis as the queue adapter, and avoid introducing a separate service for callbacks in this increment.

## Complexity Tracking

No constitution violations or additional complexity are planned.
