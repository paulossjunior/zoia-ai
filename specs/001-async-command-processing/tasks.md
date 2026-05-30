# Tasks: Async Command Processing

**Input**: Design documents from `/specs/001-async-command-processing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands-api.yaml, quickstart.md, constitution v1.0.0

**Tests**: Required by the project constitution. Test tasks are ordered after the implementation units they validate, with each test file tied to a concrete behavior.

**Organization**: Tasks are grouped by implementation slice in the exact priority requested while preserving user-story labels for traceability.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Maps implementation tasks to the relevant user story.
- Every task includes an exact file path.

## Phase 1: Project Structure

**Purpose**: Create the package skeleton and project runtime metadata before feature code.

- [X] T001 Create Python project metadata for Python 3.12, FastAPI, Uvicorn, Pydantic, redis, pytest, and httpx in `pyproject.toml`
- [X] T002 Create package marker for root application package in `app/__init__.py`
- [X] T003 [P] Create package marker for domain layer in `app/domain/__init__.py`
- [X] T004 [P] Create package marker for application layer in `app/application/__init__.py`
- [X] T005 [P] Create package marker for infrastructure layer in `app/infrastructure/__init__.py`
- [X] T006 [P] Create package marker for API layer in `app/api/__init__.py`
- [X] T007 [P] Create package marker for worker layer in `app/worker/__init__.py`
- [X] T008 [P] Create package markers for command modules in `app/commands/__init__.py` and `app/commands/test_command/__init__.py`
- [X] T009 Create shared pytest fixtures for fake queue, fake pipeline, and sample payloads in `tests/conftest.py`

**Checkpoint**: Project skeleton exists and can be imported by tests.

---

## Phase 2: Domain Entities

**Purpose**: Define framework-free command state and data structures.

- [X] T010 [US1] Create `CommandStatus` enum with queued, processing, completed, and failed values in `app/domain/status.py`
- [X] T011 [US1] Create `Command` entity with id, type, payload, status, created_at, started_at, completed_at, and error_message fields in `app/domain/command.py`
- [X] T012 [US3] Add `Command` lifecycle methods for marking processing, completed, and failed states in `app/domain/command.py`
- [X] T013 [US3] Create `CommandContext` with command, metadata, errors, result, and interruption helpers in `app/domain/context.py`
- [X] T014 [US4] Ensure `Command` failure state records safe error message and completed_at timestamp in `app/domain/command.py`

**Checkpoint**: Domain entities represent command lifecycle without imports from FastAPI, Redis, Docker, or infrastructure.

---

## Phase 3: Interfaces and Ports

**Purpose**: Define replaceable boundaries for queueing, persistence, handlers, and pipelines.

- [X] T015 [US1] Define `CommandRepository` protocol with save, get_by_id, and update methods in `app/domain/ports.py`
- [X] T016 [US1] Define `CommandQueue` protocol with publish and consume methods for command ids in `app/domain/ports.py`
- [X] T017 [US3] Define `CommandHandler` protocol that receives `CommandContext` and may interrupt processing in `app/domain/ports.py`
- [X] T018 [US3] Define `CommandPipeline` protocol that executes a command context in `app/domain/ports.py`
- [X] T019 [US3] Define base handler helpers for Chain of Responsibility implementations in `app/domain/handlers.py`

**Checkpoint**: Application code can depend on ports only, not concrete infrastructure.

---

## Phase 4: Use Cases

**Purpose**: Implement command submission and processing orchestration in the application layer.

- [X] T020 [US1] Implement `SubmitCommand` request/result dataclasses and UUID command creation in `app/application/submit_command.py`
- [X] T021 [US1] Add basic envelope validation for non-empty type and object payload in `app/application/submit_command.py`
- [X] T022 [US1] Implement persistence-before-queue behavior in `SubmitCommand` using `CommandRepository` and `CommandQueue` ports in `app/application/submit_command.py`
- [X] T023 [US3] Implement `ProcessCommand` request/result dataclasses and command lookup by id in `app/application/process_command.py`
- [X] T024 [US3] Implement `ProcessCommand` processing status update before pipeline execution in `app/application/process_command.py`
- [X] T025 [US3] Implement `ProcessCommand` completed status update after successful pipeline execution in `app/application/process_command.py`
- [X] T026 [US4] Implement `ProcessCommand` failed status update for missing commands, missing pipelines, context errors, and handler exceptions in `app/application/process_command.py`

**Checkpoint**: Core application behavior exists behind ports and can be tested without FastAPI or Redis.

---

## Phase 5: Chain of Responsibility

**Purpose**: Create reusable pipeline execution and the concrete `TEST_COMMAND` handler chain.

- [X] T027 [US3] Implement ordered `SequentialCommandPipeline` execution in `app/application/pipelines.py`
- [X] T028 [US4] Add interruption behavior to `SequentialCommandPipeline` when `CommandContext` has errors in `app/application/pipelines.py`
- [X] T029 [US3] Implement `ValidationHandler` for `TEST_COMMAND` payload structure validation in `app/commands/test_command/handlers.py`
- [X] T030 [US3] Implement `IdempotencyHandler` for `TEST_COMMAND` metadata-based duplicate prevention in `app/commands/test_command/handlers.py`
- [X] T031 [US3] Implement `BusinessCommandHandler` for `TEST_COMMAND` result generation in `app/commands/test_command/handlers.py`
- [X] T032 [US3] Implement `AuditHandler` for `TEST_COMMAND` execution metadata in `app/commands/test_command/handlers.py`
- [X] T033 [US3] Create `TEST_COMMAND` pipeline factory with handlers in validation, idempotency, business, audit order in `app/commands/test_command/pipeline.py`

**Checkpoint**: The initial command type is processed by a dedicated Chain of Responsibility pipeline.

---

## Phase 6: HandlerRegistry

**Purpose**: Keep worker orchestration generic and make command types additive.

- [X] T034 [US3] Implement `HandlerRegistry` with register and get methods keyed by command type in `app/application/handler_registry.py`
- [X] T035 [US4] Add controlled `PipelineNotFoundError` for unknown command types in `app/application/handler_registry.py`
- [X] T036 [US5] Implement default registry factory registering `TEST_COMMAND` without changing worker flow in `app/application/handler_registry.py`
- [X] T037 [US5] Add extension-oriented module docstring describing how new command types register pipelines in `app/application/handler_registry.py`

**Checkpoint**: Worker and use cases can resolve pipelines without knowing command-specific handlers.

---

## Phase 7: RedisQueueAdapter and Repository Infrastructure

**Purpose**: Implement concrete infrastructure adapters behind domain/application ports.

- [X] T038 [US1] Implement thread-safe `MemoryCommandRepository` save, get_by_id, and update methods in `app/infrastructure/memory_command_repository.py`
- [X] T039 [US3] Implement `RedisCommandQueue` constructor using REDIS_HOST, REDIS_PORT, and REDIS_QUEUE_NAME configuration in `app/infrastructure/redis_queue.py`
- [X] T040 [US1] Implement JSON command-id publication in `RedisCommandQueue.publish` in `app/infrastructure/redis_queue.py`
- [X] T041 [US3] Implement blocking JSON command-id consumption in `RedisCommandQueue.consume` in `app/infrastructure/redis_queue.py`
- [X] T042 [US4] Add safe JSON decode and queue message error logging in `app/infrastructure/redis_queue.py`
- [X] T043 [US1] Implement shared structured logging setup for APP_ENV-aware logs in `app/infrastructure/logging.py`

**Checkpoint**: Infrastructure adapters are replaceable and do not leak into domain code.

---

## Phase 8: FastAPI API

**Purpose**: Expose the command submission contract and keep HTTP behavior asynchronous.

- [X] T044 [US1] Implement Pydantic `SubmitCommandRequest` and `SubmitCommandResponse` schemas in `app/api/schemas.py`
- [X] T045 [US2] Add strict schema validation for missing type, blank type, missing payload, and non-object payload in `app/api/schemas.py`
- [X] T046 [US1] Implement `POST /commands` route returning HTTP 202 with command_id and queued status in `app/api/routes.py`
- [X] T047 [US2] Map request validation errors to HTTP 400 responses in `app/api/main.py`
- [X] T048 [US1] Wire FastAPI app, repository, queue adapter, and router dependencies in `app/api/main.py`
- [X] T049 [US1] Add submission and validation-failure logs without executing command handlers in `app/api/routes.py`

**Checkpoint**: External systems can submit commands and receive immediate acknowledgement or clear validation errors.

---

## Phase 9: Worker

**Purpose**: Consume queued commands and execute processing independently from HTTP requests.

- [X] T050 [US3] Implement worker dependency factory for repository, Redis queue, and default handler registry in `app/worker/main.py`
- [X] T051 [US3] Implement single-iteration worker function that consumes one command id and calls `ProcessCommand` in `app/worker/main.py`
- [X] T052 [US3] Implement continuous worker loop with graceful logging around each iteration in `app/worker/main.py`
- [X] T053 [US4] Add worker failure logging for unknown pipeline, handler exception, and invalid payload outcomes in `app/worker/main.py`
- [X] T054 [US3] Ensure worker contains no command-type-specific branching beyond registry composition in `app/worker/main.py`

**Checkpoint**: Processing happens in a worker process and command-type behavior stays inside pipelines.

---

## Phase 10: Docker Compose

**Purpose**: Provide local runtime with separate API, worker, and Redis services.

- [X] T055 Create Docker image build for API and worker using Python 3.12 and project dependencies in `Dockerfile`
- [X] T056 Create `redis` service with Redis default port in `docker-compose.yml`
- [X] T057 Create `api` service running `uvicorn app.api.main:app --host 0.0.0.0 --port 8000` with Redis environment variables in `docker-compose.yml`
- [X] T058 Create `worker` service running `python -m app.worker.main` with Redis environment variables in `docker-compose.yml`
- [X] T059 Add service dependency ordering so API and worker wait for Redis service availability in `docker-compose.yml`

**Checkpoint**: Docker Compose can launch separate API, worker, and Redis services using the same codebase.

---

## Phase 11: Automated Tests

**Purpose**: Validate the full behavior required by the spec, plan, and constitution.

- [X] T060 [US1] Test `POST /commands` valid request returns 202, UUID command_id, and queued status in `tests/test_api.py`
- [X] T061 [US2] Test `POST /commands` missing type, blank type, missing payload, non-object payload, and malformed JSON return 400 in `tests/test_api.py`
- [X] T062 [US1] Test API route does not execute command handlers during submission in `tests/test_api.py`
- [X] T063 [US1] Test `SubmitCommand` creates command, persists before queueing, and publishes command id in `tests/test_submit_command.py`
- [X] T064 [US2] Test `SubmitCommand` invalid envelope does not persist or enqueue command in `tests/test_submit_command.py`
- [X] T065 [US3] Test `ProcessCommand` consumes known command type and transitions queued to processing to completed in `tests/test_process_command.py`
- [X] T066 [US4] Test `ProcessCommand` unknown command type marks command failed with safe error message in `tests/test_process_command.py`
- [X] T067 [US4] Test handler exception marks command failed with completed_at and error_message in `tests/test_process_command.py`
- [X] T068 [US3] Test worker single iteration consumes queue message and invokes `ProcessCommand` in `tests/test_worker.py`
- [X] T069 [US3] Test `RedisCommandQueue` serializes and deserializes JSON command id messages using fake Redis client in `tests/test_worker.py`
- [X] T070 [US3] Test Chain of Responsibility handlers execute in Validation, Idempotency, Business, Audit order in `tests/test_chain_of_responsibility.py`
- [X] T071 [US4] Test invalid payload interrupts Chain of Responsibility before `BusinessCommandHandler` in `tests/test_chain_of_responsibility.py`
- [X] T072 [US3] Test `CommandContext` metadata, errors, and result are shared across handlers in `tests/test_chain_of_responsibility.py`
- [X] T073 [US5] Test registering a new command type executes a new pipeline without worker changes in `tests/test_process_command.py`
- [X] T074 [US1] Test domain layer has no imports from FastAPI, Redis, Docker, or infrastructure modules in `tests/test_architecture.py`
- [X] T075 Run full automated test suite with pytest and fix failures discovered by `pytest`

**Checkpoint**: Automated tests cover success, validation, worker, failures, Chain of Responsibility, extensibility, and architectural boundaries.

---

## Phase 12: README and Execution Instructions

**Purpose**: Document how to run, test, and extend the service.

- [X] T076 Document project purpose, architecture layers, and asynchronous command flow in `README.md`
- [X] T077 Document local Python setup and pytest execution in `README.md`
- [X] T078 Document Docker Compose startup for api, worker, and redis services in `README.md`
- [X] T079 Document `POST /commands` request, 202 response, and 400 validation errors with curl examples in `README.md`
- [X] T080 Document worker logs and expected command lifecycle statuses in `README.md`
- [X] T081 Document how to add a new command type by creating a pipeline and registering it in `HandlerRegistry` in `README.md`

**Checkpoint**: A developer can run the service, submit a command, observe worker processing, run tests, and add a new command type from README instructions.

---

## Dependencies & Execution Order

### Ordered Priority

1. Project structure: T001-T009
2. Domain entities: T010-T014
3. Interfaces/ports: T015-T019
4. Use cases: T020-T026
5. Chain of Responsibility: T027-T033
6. HandlerRegistry: T034-T037
7. RedisQueueAdapter and repository infrastructure: T038-T043
8. FastAPI API: T044-T049
9. Worker: T050-T054
10. Docker Compose: T055-T059
11. Automated tests: T060-T075
12. README: T076-T081

### User Story Coverage

- **US1 Submit Valid Command**: T010-T011, T015-T016, T020-T022, T038, T040, T043-T044, T046, T048-T049, T060, T062-T063, T074
- **US2 Reject Invalid Command**: T021, T045, T047, T061, T064
- **US3 Process Queued Command**: T012-T013, T017-T019, T023-T025, T027, T029-T034, T036, T039, T041, T050-T052, T054, T065, T068-T070, T072
- **US4 Record Processing Failure**: T014, T026, T028, T035, T042, T053, T066-T067, T071
- **US5 Add New Command Handler**: T036-T037, T073, T081

### Parallel Opportunities

- Package marker tasks T003-T008 can run in parallel.
- Domain files T010, T011, and T013 can be drafted in parallel after T002.
- Ports T015-T018 can be implemented together in `app/domain/ports.py` before use cases.
- Chain handlers T029-T032 can be implemented in parallel in `app/commands/test_command/handlers.py` after T027.
- Docker tasks T055-T059 can run after API/worker entrypoints are known.
- Independent tests T060-T074 can be split by test file once implementation files exist.

## Independent Test Criteria

- **US1**: Valid `POST /commands` returns `202`, UUID `command_id`, and `queued`, with command persisted before queue publication and no handler execution.
- **US2**: Invalid requests return `400` before command creation or queue publication.
- **US3**: Worker processes a queued `TEST_COMMAND`, resolves the registered pipeline, executes handlers in order, and marks command `completed`.
- **US4**: Unknown command type, invalid payload, or handler exception marks command `failed` with `completed_at` and safe `error_message`.
- **US5**: A new command type can be registered and processed without modifying the worker loop or API route.

## Implementation Strategy

### MVP First

Complete T001-T049, then T060-T064 and T074. This yields a safe HTTP boundary that accepts valid commands, rejects invalid commands, and guarantees the API does not process business handlers directly.

### Full Async Flow

Complete T050-T075 after MVP to enable Redis-backed worker consumption, pipeline execution, success/failure lifecycle tracking, and architecture verification.

### Finalization

Complete T076-T081 after tests pass so README instructions match the implemented behavior exactly.
