# Implementation Plan: Async Command Processing

**Branch**: `001-async-command-processing` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-async-command-processing/spec.md` plus copied implementation context for Python, FastAPI, Redis, Docker, worker, and Chain of Responsibility.

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a Python 3.12 web service that accepts external commands at `POST /commands`, validates the generic command envelope, records the command, enqueues it through a queue abstraction backed by Redis, and returns `202 Accepted` with `command_id` and `queued` status. Independent Python workers consume queued command identifiers, load the command from a repository abstraction, resolve a `CommandPipeline` by `type`, execute handlers through Chain of Responsibility, and persist final status as `completed` or `failed`.

The first implementation will bootstrap the application codebase with domain/application/infrastructure/API/worker layers, an in-memory command repository for v1, a Redis queue adapter, a `TEST_COMMAND` pipeline, Docker Compose services, and automated tests that prove the API does not execute command business logic directly.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic, redis-py, Uvicorn  
**Storage**: In-memory `CommandRepository` for v1; Redis used only as queue broker through `CommandQueue` adapter  
**Testing**: Pytest with FastAPI test client/httpx-style request testing and adapter/memory fakes  
**Target Platform**: Docker Compose local environment with separate Linux containers for API, worker, and Redis  
**Project Type**: Web service with independent background worker  
**Performance Goals**: 95% of accepted command submissions acknowledge within 500 ms under normal local/dev load; client never waits for command-specific handler execution  
**Constraints**: Domain layer must not import FastAPI, Redis, Docker, databases, or external service libraries; Redis and repository implementations must sit behind application/domain interfaces; worker must not contain command-type-specific logic  
**Scale/Scope**: v1 includes one functional `TEST_COMMAND` pipeline, documents `SEND_EMAIL` and `GENERATE_REPORT` as future examples, and uses an in-memory repository that is replaceable by PostgreSQL later

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. Planned source layout separates `app/domain`, `app/application`, `app/infrastructure`, `app/api`, `app/worker`, and `app/commands`. Domain owns entities, statuses, context, and ports only.
- **Asynchronous command flow**: PASS. HTTP validates, records, enqueues, and returns `202`; command-specific processing occurs only in the worker via `ProcessCommand`.
- **Explicit contracts**: PASS. `contracts/commands-api.yaml` defines request, response, validation errors, and state enum. `data-model.md` defines entities and lifecycle transitions.
- **Infrastructure abstraction**: PASS. Redis is accessed only by `RedisCommandQueue`, implementing `CommandQueue`; command persistence goes through `CommandRepository`, initially `MemoryCommandRepository`.
- **Observability**: PASS. Plan requires logs for submission, worker start, command success, command failure, and unregistered pipeline errors; status transitions are persisted on every command.
- **Testing discipline**: PASS. Test plan includes API success/validation, submit use case, worker/process use case, handler failure, payload validation interruption, queue adapter/fake integration, and proof that API does not execute handlers directly.
- **Handler extensibility**: PASS. New command types require a new pipeline and registration in `HandlerRegistry`; worker flow stays unchanged.

Post-design re-check: PASS. The generated research, data model, API contract, and quickstart preserve the same abstractions and contain no justified constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-async-command-processing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── commands-api.yaml
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py
│   ├── status.py
│   ├── ports.py
│   ├── handlers.py
│   └── context.py
├── application/
│   ├── submit_command.py
│   ├── process_command.py
│   ├── handler_registry.py
│   └── pipelines.py
├── infrastructure/
│   ├── redis_queue.py
│   ├── memory_command_repository.py
│   └── logging.py
├── api/
│   ├── main.py
│   ├── schemas.py
│   └── routes.py
├── worker/
│   └── main.py
└── commands/
    └── test_command/
        ├── pipeline.py
        └── handlers.py

tests/
├── test_api.py
├── test_submit_command.py
├── test_process_command.py
├── test_worker.py
└── test_chain_of_responsibility.py

Dockerfile
docker-compose.yml
pyproject.toml
README.md
```

**Structure Decision**: Use the user-specified `app/` package layout rather than the generic `src/` template so API and worker can share one codebase while preserving constitution-required boundaries.

## Complexity Tracking

No constitution violations or unjustified complexity are planned.
