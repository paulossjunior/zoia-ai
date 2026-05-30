# Implementation Plan: Command Status Query

**Branch**: `003-command-status-query` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-command-status-query/spec.md`

## Summary

Add a read-only command status lookup to the asynchronous command service through `GET /commands/{command_id}`. The endpoint will reuse the existing command repository abstraction to fetch a command by id, validate identifier format before lookup, return a public status view without the original payload, and document success, invalid id, and not-found responses in the generated API documentation.

## Technical Context

**Language/Version**: Python 3.12 target runtime; current local tests may execute with the active virtualenv interpreter  
**Primary Dependencies**: Existing FastAPI, Pydantic, Redis adapter, and pytest stack; no new runtime dependency required  
**Storage**: Existing command repository port with Redis-backed runtime repository and in-memory test repository  
**Testing**: Pytest with FastAPI TestClient, application use case tests, repository mock/fake tests, and documentation checks  
**Target Platform**: Existing Docker Compose local environment with API, worker, and Redis  
**Project Type**: Web service plus worker  
**Performance Goals**: Status lookup should return from the existing command store without queue interaction and be fast enough for normal polling workflows  
**Constraints**: Lookup must be read-only, must not enqueue or execute command processing, must not return original payload by default, and must not expose queue or storage implementation details to clients  
**Scale/Scope**: Covers one new status query endpoint, one read-only application use case, response/error schemas, OpenAPI docs, tests, and README updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. The existing `Command` entity and `CommandStatus` remain in `app/domain`; status lookup adds no domain dependency on FastAPI, Redis, storage, or queue code.
- **Asynchronous command flow**: PASS. This feature observes command state only. It does not create work, enqueue work, or run handlers during HTTP requests.
- **Explicit contracts**: PASS. The feature defines request path parameter validation, success response, invalid identifier error, not-found error, and explicit status values.
- **Infrastructure abstraction**: PASS. The endpoint will access command state through the existing `CommandRepository` port; Redis remains an infrastructure adapter detail.
- **Observability**: PASS. Lookup attempts, validation failures, not-found outcomes, and successful reads should be logged without changing command status.
- **Testing discipline**: PASS. Tests will cover success paths, invalid id, not found, failed command visibility, no payload leakage, no queue publication, no handler execution, OpenAPI docs, and architecture boundaries.
- **Handler extensibility**: PASS. No new command type is introduced. Existing handler registry and worker flow remain unchanged.

Post-design re-check: PASS. The research, model, contracts, and quickstart preserve layered architecture, read-only behavior, explicit contracts, and test coverage without adding new infrastructure coupling.

## Project Structure

### Documentation (this feature)

```text
specs/003-command-status-query/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── command-status-contract.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py       # Reuse Command entity and lifecycle timestamps
│   ├── status.py        # Reuse explicit command states
│   └── ports.py         # Reuse CommandRepository port
├── application/
│   └── get_command_status.py
├── api/
│   ├── main.py          # Preserve HTTP 400 validation behavior
│   ├── schemas.py       # Add status and error response schemas
│   └── routes.py        # Add GET /commands/{command_id}
├── infrastructure/
│   ├── redis_command_repository.py
│   └── memory_command_repository.py
└── worker/
    └── main.py          # No change to worker orchestration

tests/
├── test_api.py
├── test_get_command_status.py
├── test_documentation.py
└── test_architecture.py

README.md
```

**Structure Decision**: Update the existing layered service in place. Add a small application use case for read-only status lookup so the API does not reach directly into adapter internals and the command repository remains replaceable.

## Complexity Tracking

No constitution violations or additional complexity are planned.
