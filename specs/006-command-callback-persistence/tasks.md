# Tasks: Command Callback Persistence

**Input**: Design documents from `/specs/006-command-callback-persistence/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`
**Tests**: Required by the project constitution. Test tasks appear before implementation tasks for each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase because it touches different files or independent test coverage.
- **[Story]**: User story covered by the task (`US1`, `US2`, `US3`, `US4`).
- Every task includes exact file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current project baseline and prepare shared dependencies/configuration for the callback persistence feature.

- [X] T001 Inspect current command model, status enum, ports, repositories, API routes, worker wiring, and Docker services in `app/domain/command.py`, `app/domain/status.py`, `app/domain/ports.py`, `app/infrastructure/redis_command_repository.py`, `app/infrastructure/memory_command_repository.py`, `app/api/routes.py`, `app/worker/main.py`, and `docker-compose.yml`.
- [X] T002 Run the current test suite with `.venv/bin/pytest` and record baseline failures, if any, in `specs/006-command-callback-persistence/tasks.md`.
- [X] T003 [P] Add PostgreSQL and HTTP callback runtime dependencies to `pyproject.toml`.
- [X] T004 [P] Add PostgreSQL environment variable names to `README.md` and keep existing Redis variables documented in `README.md`.
- [X] T005 [P] Add callback persistence quickstart references to `README.md` based on `specs/006-command-callback-persistence/quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared domain fields, ports, fake adapters, and configuration used by all user stories.

**CRITICAL**: No user story implementation should start until these foundational tasks are complete.

- [X] T006 [P] Add architecture tests proving `app/domain/` does not import FastAPI, Redis, PostgreSQL, Docker, or HTTP clients in `tests/test_architecture.py`.
- [X] T007 [P] Add reusable test builders for commands with `external_id`, `callback`, callback status, response payload, and callback errors in `tests/conftest.py`.
- [X] T008 [P] Add `CallbackStatus` enum with `not_required`, `pending`, `sent`, and `failed` in `app/domain/status.py`.
- [X] T009 Extend `CommandRepository` with latest-by-external-id lookup and callback audit update expectations in `app/domain/ports.py`.
- [X] T010 Add `CallbackClient` port for callback delivery in `app/domain/ports.py`.
- [X] T011 Extend `Command` with `external_id`, `callback`, `response_payload`, `callback_status`, `callback_error_message`, `retry_count`, and `callback_sent_at` in `app/domain/command.py`.
- [X] T012 Add domain lifecycle methods for callback required, callback sent, and callback failed transitions in `app/domain/command.py`.
- [X] T013 Update `CommandContext` usage or result conventions so pipelines expose response payloads through `app/domain/context.py`.
- [X] T014 Update `MemoryCommandRepository` to store and retrieve all new command and callback fields in `app/infrastructure/memory_command_repository.py`.
- [X] T015 Update Redis-backed command repository serialization for all new fields in `app/infrastructure/redis_command_repository.py`.
- [X] T016 [P] Add PostgreSQL service, healthcheck, database variables, and service dependencies to `docker-compose.yml`.
- [X] T017 [P] Add PostgreSQL configuration defaults to `app/api/main.py` and `app/worker/main.py` without importing PostgreSQL code into `app/domain/`.
- [X] T018 [P] Add documentation checks for callback fields and PostgreSQL persistence references in `tests/test_documentation.py`.

**Checkpoint**: Foundation ready - user stories can now be implemented and tested independently.

---

## Phase 3: User Story 1 - Submit Traceable Async Command (Priority: P1) MVP

**Goal**: Accept `type`, `payload`, optional `external_id`, and optional `callback`; persist the command before queueing; return `command_id` and `queued` immediately.

**Independent Test**: Submit valid commands with and without optional fields, then verify the response and persisted command state without running any processing pipeline.

### Tests for User Story 1

- [X] T019 [P] [US1] Add API test for minimal `POST /commands` returning `202`, `command_id`, and `queued` in `tests/test_api.py`.
- [X] T020 [P] [US1] Add API test for full `POST /commands` persisting `external_id`, `callback`, and `callback_status=pending` in `tests/test_api.py`.
- [X] T021 [P] [US1] Add API test proving omitted, null, and blank callback values persist `callback_status=not_required` in `tests/test_api.py`.
- [X] T022 [P] [US1] Add API validation tests for missing `type`, blank `type`, missing `payload`, and non-object `payload` returning HTTP 400 in `tests/test_api.py`.
- [X] T023 [P] [US1] Add `SubmitCommand` test proving persistence happens before queue publication in `tests/test_submit_command.py`.
- [X] T024 [P] [US1] Add `SubmitCommand` test proving invalid submissions do not persist or enqueue commands in `tests/test_submit_command.py`.
- [X] T025 [P] [US1] Add test proving API submission does not execute command handlers or pipelines in `tests/test_api.py`.
- [X] T026 [P] [US1] Add PostgreSQL repository test for inserting and reading queued commands with JSON payloads and optional callback fields in `tests/test_postgres_command_repository.py`.

### Implementation for User Story 1

- [X] T027 [US1] Extend command request and response schemas with `external_id`, `callback`, `command_id`, and validation examples in `app/api/schemas.py`.
- [X] T028 [US1] Update API validation error handling for invalid command requests in `app/api/routes.py`.
- [X] T029 [US1] Update `SubmitCommand` input and output models for `external_id`, `callback`, and callback initial status in `app/application/submit_command.py`.
- [X] T030 [US1] Ensure `SubmitCommand` persists the command before enqueueing the command id in `app/application/submit_command.py`.
- [X] T031 [US1] Create PostgreSQL command repository adapter with table initialization and insert/get support in `app/infrastructure/postgres_command_repository.py`.
- [X] T032 [US1] Wire API runtime to PostgreSQL repository and Redis queue using environment variables in `app/api/main.py`.
- [X] T033 [US1] Keep test-time dependency overrides for repository and queue in `app/api/routes.py`.
- [X] T034 [US1] Update OpenAPI metadata and request/response examples for `POST /commands` in `app/api/main.py`.
- [X] T035 [US1] Update `docker-compose.yml` so `api` depends on healthy `postgres` and `redis`.
- [X] T036 [US1] Run focused US1 tests with `.venv/bin/pytest tests/test_api.py tests/test_submit_command.py tests/test_postgres_command_repository.py`.

**Checkpoint**: US1 is independently functional: commands can be accepted, persisted, queued, and returned without processing.

---

## Phase 4: User Story 2 - Process Command and Persist Outcome (Priority: P2)

**Goal**: Worker processing loads persisted commands, marks processing, resolves the pipeline by type, persists response payload on success, and persists error message on failure.

**Independent Test**: Process queued commands through success, handler failure, and missing-pipeline paths, then verify persisted status, timestamps, response payload, and error message.

### Tests for User Story 2

- [X] T037 [P] [US2] Add `ProcessCommand` success test verifying `processing`, `completed`, `response_payload`, and timestamps in `tests/test_process_command.py`.
- [X] T038 [P] [US2] Add `ProcessCommand` handler failure test verifying `failed`, `error_message`, and finish timestamp in `tests/test_process_command.py`.
- [X] T039 [P] [US2] Add missing-pipeline test verifying a clear failed status and error message in `tests/test_process_command.py`.
- [X] T040 [P] [US2] Add worker test proving it consumes a queue message, delegates to `ProcessCommand`, and contains no type-specific branching in `tests/test_worker.py`.
- [X] T041 [P] [US2] Add Chain of Responsibility test proving response data from `BusinessCommandHandler` is shared through context in `tests/test_chain_of_responsibility.py`.
- [X] T042 [P] [US2] Add PostgreSQL repository test for updating processing status, final success response, final failure error, and timestamps in `tests/test_postgres_command_repository.py`.

### Implementation for User Story 2

- [X] T043 [US2] Update `Command` processing lifecycle methods to set `processing_started_at`, `processing_finished_at`, `response_payload`, and `error_message` in `app/domain/command.py`.
- [X] T044 [US2] Update `ProcessCommand` to load persisted commands by id before pipeline execution in `app/application/process_command.py`.
- [X] T045 [US2] Update `ProcessCommand` to persist `processing`, `completed`, and `failed` transitions with clear logs in `app/application/process_command.py`.
- [X] T046 [US2] Update `HandlerRegistry` error handling for unknown command types in `app/application/handler_registry.py`.
- [X] T047 [US2] Update pipeline execution to return or expose response payloads consistently in `app/application/pipelines.py`.
- [X] T048 [US2] Update TEST_COMMAND handlers to populate `CommandContext.result` and respect validation failures in `app/commands/test_command/handlers.py`.
- [X] T049 [US2] Update TEST_COMMAND pipeline composition only inside the command-specific module in `app/commands/test_command/pipeline.py`.
- [X] T050 [US2] Update PostgreSQL repository update methods for processing, success, and failure states in `app/infrastructure/postgres_command_repository.py`.
- [X] T051 [US2] Wire worker runtime to PostgreSQL repository, Redis queue, and registry without type-specific logic in `app/worker/main.py`.
- [X] T052 [US2] Run focused US2 tests with `.venv/bin/pytest tests/test_process_command.py tests/test_worker.py tests/test_chain_of_responsibility.py tests/test_postgres_command_repository.py`.

**Checkpoint**: US2 is independently functional: queued commands reach `completed` or `failed` with persisted audit data.

---

## Phase 5: User Story 3 - Deliver Optional Callback (Priority: P3)

**Goal**: After processing reaches a final status, send a callback only when configured, audit callback success/failure, and preserve the command processing outcome.

**Independent Test**: Process commands with success callbacks, failure callbacks, no callbacks, and callback delivery failures, then verify callback status fields and command status isolation.

### Tests for User Story 3

- [X] T053 [P] [US3] Add callback payload contract tests for success and failure payload shapes in `tests/test_callback_delivery.py`.
- [X] T054 [P] [US3] Add test proving completed commands with callback send one callback request and persist `callback_status=sent` in `tests/test_callback_delivery.py`.
- [X] T055 [P] [US3] Add test proving failed commands with callback send one callback request containing the error payload in `tests/test_callback_delivery.py`.
- [X] T056 [P] [US3] Add test proving commands without callback do not call the callback client and persist `callback_status=not_required` in `tests/test_callback_delivery.py`.
- [X] T057 [P] [US3] Add test proving callback delivery failure sets `callback_status=failed`, stores `callback_error_message`, increments `retry_count`, and preserves command `status` in `tests/test_callback_delivery.py`.
- [X] T058 [P] [US3] Add HTTP callback adapter test for successful 2xx and unsuccessful non-2xx responses in `tests/test_callback_delivery.py`.
- [X] T059 [P] [US3] Add PostgreSQL repository test for callback sent and callback failed audit fields in `tests/test_postgres_command_repository.py`.

### Implementation for User Story 3

- [X] T060 [US3] Add callback delivery orchestration after final processing status in `app/application/process_command.py`.
- [X] T061 [US3] Add helper to build callback success and failure payloads from `Command` in `app/application/process_command.py`.
- [X] T062 [US3] Add no-op behavior for missing, null, or blank callback values in `app/application/process_command.py`.
- [X] T063 [US3] Implement HTTP callback client adapter with timeout, non-2xx handling, and clear error messages in `app/infrastructure/http_callback_client.py`.
- [X] T064 [US3] Update `Command` callback lifecycle methods for sent and failed audit states in `app/domain/command.py`.
- [X] T065 [US3] Update `MemoryCommandRepository` to persist callback sent and failed transitions in `app/infrastructure/memory_command_repository.py`.
- [X] T066 [US3] Update `RedisCommandRepository` compatibility for callback status fields if retained for local tests in `app/infrastructure/redis_command_repository.py`.
- [X] T067 [US3] Update `PostgresCommandRepository` to persist callback sent and failed transitions in `app/infrastructure/postgres_command_repository.py`.
- [X] T068 [US3] Wire worker runtime to inject the HTTP callback client into processing in `app/worker/main.py`.
- [X] T069 [US3] Add callback attempt, success, and failure logs in `app/infrastructure/logging.py`.
- [X] T070 [US3] Run focused US3 tests with `.venv/bin/pytest tests/test_callback_delivery.py tests/test_process_command.py tests/test_postgres_command_repository.py`.

**Checkpoint**: US3 is independently functional: callbacks are delivered only when requested and audited separately from command processing.

---

## Phase 6: User Story 4 - Query Commands by Command or External Identifier (Priority: P4)

**Goal**: Query full command details, status-only data, and the most recent command for an external business id.

**Independent Test**: Create persisted commands with different ids, statuses, and repeated external ids, then verify command-id lookup, status lookup, latest external-id lookup, and not-found errors.

### Tests for User Story 4

- [X] T071 [P] [US4] Add `GET /commands/{command_id}` API test returning full command data with callback audit fields in `tests/test_get_command.py`.
- [X] T072 [P] [US4] Add `GET /commands/{command_id}/status` API test returning only `command_id`, `status`, and `callback_status` in `tests/test_get_command_status.py`.
- [X] T073 [P] [US4] Add `GET /commands/external/{external_id}` API test returning the most recent command by request receipt time in `tests/test_get_command_by_external_id.py`.
- [X] T074 [P] [US4] Add not-found and invalid-command-id API tests for command id, status, and external id lookups in `tests/test_api.py`.
- [X] T075 [P] [US4] Add repository tests for latest-by-external-id ordering in memory and PostgreSQL repositories in `tests/test_get_command_by_external_id.py` and `tests/test_postgres_command_repository.py`.

### Implementation for User Story 4

- [X] T076 [US4] Update command detail response schemas to use `command_id`, `response_payload`, callback fields, and lifecycle timestamps in `app/api/schemas.py`.
- [X] T077 [US4] Update status response schema to include `callback_status` in `app/api/schemas.py`.
- [X] T078 [US4] Add external-id lookup response schema and examples in `app/api/schemas.py`.
- [X] T079 [US4] Update `GetCommand` mapping to return full callback persistence fields in `app/application/get_command.py`.
- [X] T080 [US4] Update `GetCommandStatus` mapping to return `command_id`, `status`, and `callback_status` in `app/application/get_command_status.py`.
- [X] T081 [US4] Create `GetCommandByExternalId` use case returning the latest matching command in `app/application/get_command_by_external_id.py`.
- [X] T082 [US4] Add route ordering for `GET /commands/external/{external_id}` before `GET /commands/{command_id}` in `app/api/routes.py`.
- [X] T083 [US4] Update `GET /commands/{command_id}` and `GET /commands/{command_id}/status` routes with 400 and 404 handling in `app/api/routes.py`.
- [X] T084 [US4] Implement latest-by-external-id lookup in `MemoryCommandRepository` in `app/infrastructure/memory_command_repository.py`.
- [X] T085 [US4] Implement latest-by-external-id lookup and indexes in `PostgresCommandRepository` in `app/infrastructure/postgres_command_repository.py`.
- [X] T086 [US4] Update OpenAPI endpoint descriptions for command detail, status, and external-id lookup in `app/api/main.py`.
- [X] T087 [US4] Run focused US4 tests with `.venv/bin/pytest tests/test_get_command.py tests/test_get_command_status.py tests/test_get_command_by_external_id.py tests/test_api.py`.

**Checkpoint**: US4 is independently functional: command records can be queried by command id, status endpoint, and latest external id.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, operational validation, and whole-system verification.

- [X] T088 [P] Update `README.md` with PostgreSQL persistence, callback submission examples, query examples, RedisInsight usage, and Docker Compose commands.
- [X] T089 [P] Add an ADR for PostgreSQL command persistence and callback audit separation in `docs/adr/0009-command-callback-persistence.md`.
- [X] T090 [P] Update existing ADR references for Redis queue-only behavior in `docs/adr/0004-redis-local-adapter.md`.
- [X] T091 [P] Update `specs/006-command-callback-persistence/quickstart.md` if implementation commands or environment variables changed.
- [X] T092 Run the full test suite with `.venv/bin/pytest` and fix regressions in the files reported by pytest.
- [X] T093 Run Docker Compose validation for API, worker, Redis, RedisInsight, and PostgreSQL using `docker compose up --build` against `docker-compose.yml`.
- [X] T094 Verify the quickstart flow manually with `curl` commands against `POST /commands`, `GET /commands/{command_id}`, `GET /commands/{command_id}/status`, and `GET /commands/external/{external_id}` from `specs/006-command-callback-persistence/quickstart.md`.
- [X] T095 Verify Swagger/OpenAPI exposes the new request and response schemas at `/docs` using `app/api/main.py`.
- [X] T096 Run final architecture checks with `.venv/bin/pytest tests/test_architecture.py tests/test_documentation.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; blocks every user story.
- **Phase 3 US1**: Depends on Phase 2; MVP scope.
- **Phase 4 US2**: Depends on Phase 2 and integrates naturally after US1 persistence exists.
- **Phase 5 US3**: Depends on Phase 2 and final processing states from US2.
- **Phase 6 US4**: Depends on Phase 2 and can be implemented after persisted fields exist from US1.
- **Phase 7 Polish**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Required MVP. Delivers traceable submission and durable persistence before queueing.
- **US2 (P2)**: Requires persisted command records from US1 for runtime processing; can be tested with direct repository fixtures.
- **US3 (P3)**: Requires US2 final processing outcomes; callback delivery is post-processing behavior.
- **US4 (P4)**: Requires persisted fields from US1 and can be implemented partly in parallel with US2 once repository methods exist.

### Within Each User Story

- Write and run tests first when practical; they should fail before implementation.
- Domain model and ports before use cases.
- Use cases before API or worker wiring.
- Infrastructure adapters behind ports only.
- Story is complete only when focused tests pass.

---

## Parallel Opportunities

- Setup tasks T003-T005 can run in parallel.
- Foundational tasks T006-T008 and T016-T018 can run in parallel after T001.
- US1 tests T019-T026 can run in parallel before implementation.
- US2 tests T037-T042 can run in parallel before implementation.
- US3 tests T053-T059 can run in parallel before implementation.
- US4 tests T071-T075 can run in parallel before implementation.
- Documentation/ADR polish tasks T088-T091 can run in parallel after story implementation stabilizes.

---

## Parallel Example: US1

```bash
# API and use-case tests can be created independently:
Task: "T019 [P] [US1] Add API test for minimal POST /commands returning 202..."
Task: "T023 [P] [US1] Add SubmitCommand test proving persistence happens before queue publication..."
Task: "T026 [P] [US1] Add PostgreSQL repository test for inserting and reading queued commands..."
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 (US1). This proves the system can accept traceable commands, persist them durably, enqueue them, and return immediately.

### Incremental Delivery

1. Deliver US1 and run focused submission tests.
2. Deliver US2 and run processing/worker tests.
3. Deliver US3 and run callback delivery tests.
4. Deliver US4 and run query tests.
5. Finish Phase 7 and run the full suite plus Docker Compose validation.
