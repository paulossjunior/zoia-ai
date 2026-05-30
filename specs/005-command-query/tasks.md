# Tasks: Command Query

**Input**: Design documents from `/specs/005-command-query/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/command-query-contract.md`, `quickstart.md`

**Tests**: Tests are REQUIRED by the project constitution. Test tasks are listed before implementation tasks for each user story and cover success paths, validation errors, not-found errors, repository adapter behavior, read-only API behavior, and documentation contracts.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current query behavior and repository shape before widening contracts.

- [X] T001 Inspect existing command retrieval use case and API route behavior in `app/application/get_command_status.py` and `app/api/routes.py`
- [X] T002 Inspect existing public response schemas and OpenAPI tests in `app/api/schemas.py` and `tests/test_documentation.py`
- [X] T003 Inspect repository port and adapter capabilities for single-record reads and future list queries in `app/domain/ports.py`, `app/infrastructure/memory_command_repository.py`, and `app/infrastructure/redis_command_repository.py`
- [X] T004 Run the current test suite to capture the pre-change baseline for `tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared contract expectations and repository query primitives required by all query stories.

**CRITICAL**: No user story implementation should begin until foundational contracts and adapter expectations are clear.

- [X] T005 [P] Add shared command fixture helpers for queued, completed, failed, and processing records in `tests/conftest.py`
- [X] T006 [P] Add documentation contract constants for command detail, status-only, list, and error examples in `tests/test_documentation.py`
- [X] T007 [P] Add architecture regression coverage for read-only query APIs not importing infrastructure into domain modules in `tests/test_architecture.py`
- [X] T008 Extend `CommandRepository` with a list/query method signature for status-filtered pagination in `app/domain/ports.py`
- [X] T009 Update MemoryCommandRepository to support deterministic command listing ordered by request receipt time in `app/infrastructure/memory_command_repository.py`
- [X] T010 Update RedisCommandRepository to support deterministic command listing ordered by request receipt time in `app/infrastructure/redis_command_repository.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Complete Command Details (Priority: P1) MVP

**Goal**: Return the complete persisted command details by identifier with id, type, status, payload, response, error, and lifecycle timestamps.

**Independent Test**: Query a known command id and verify the response matches the complete command detail contract; query an unknown id and verify a 404.

### Tests for User Story 1

- [X] T011 [P] [US1] Add full detail use case tests for queued, completed, failed, and processing records in `tests/test_get_command.py`
- [X] T012 [P] [US1] Add full detail use case tests for malformed id and unknown command errors in `tests/test_get_command.py`
- [X] T013 [P] [US1] Add API tests for `GET /commands/{id}` returning full details with `id` field and no `command_id` field in `tests/test_api.py`
- [X] T014 [P] [US1] Add API tests for `GET /commands/{id}` malformed id returning 400 and unknown id returning 404 in `tests/test_api.py`
- [X] T015 [P] [US1] Add API read-only guard test proving full detail lookup does not enqueue, consume queue messages, or execute handlers in `tests/test_api.py`
- [X] T016 [P] [US1] Add OpenAPI documentation tests for the full command detail response and error contracts in `tests/test_documentation.py`

### Implementation for User Story 1

- [X] T017 [US1] Create `GetCommand` request/result/errors for full command detail lookup in `app/application/get_command.py`
- [X] T018 [US1] Map persisted Command fields to the full detail result with external field `id` in `app/application/get_command.py`
- [X] T019 [US1] Add full command detail response schema using `id`, payload, response, error, and lifecycle timestamps in `app/api/schemas.py`
- [X] T020 [US1] Wire `GetCommand` into the FastAPI app state in `app/api/main.py`
- [X] T021 [US1] Update `GET /commands/{id}` route to use `GetCommand`, return the full detail schema, and preserve 400/404 behavior in `app/api/routes.py`
- [X] T022 [US1] Add read-only success, invalid id, and not-found logs for full command lookup in `app/api/routes.py`

**Checkpoint**: User Story 1 is functional when full details can be retrieved by id without queue or handler side effects.

---

## Phase 4: User Story 2 - Retrieve Current Command Status Only (Priority: P2)

**Goal**: Return only id and status for a command by identifier.

**Independent Test**: Query a known command through `/commands/{id}/status` and verify the response contains exactly id and status.

### Tests for User Story 2

- [X] T023 [P] [US2] Update status use case tests to assert status-only result includes exactly id and status in `tests/test_get_command_status.py`
- [X] T024 [P] [US2] Add status use case tests for malformed id and unknown command errors in `tests/test_get_command_status.py`
- [X] T025 [P] [US2] Add API tests for `GET /commands/{id}/status` across queued, processing, completed, and failed statuses in `tests/test_api.py`
- [X] T026 [P] [US2] Add API tests proving status-only response omits payload, response, error message, and timestamps in `tests/test_api.py`
- [X] T027 [P] [US2] Add API read-only guard test proving status lookup does not enqueue, consume queue messages, or execute handlers in `tests/test_api.py`
- [X] T028 [P] [US2] Add OpenAPI documentation tests for the status-only response and error contracts in `tests/test_documentation.py`

### Implementation for User Story 2

- [X] T029 [US2] Refactor `GetCommandStatusResult` to expose only `id` and `status` in `app/application/get_command_status.py`
- [X] T030 [US2] Add status-only response schema with exactly `id` and `status` in `app/api/schemas.py`
- [X] T031 [US2] Add `GET /commands/{id}/status` route using `GetCommandStatus` in `app/api/routes.py`
- [X] T032 [US2] Add read-only success, invalid id, and not-found logs for status lookup in `app/api/routes.py`
- [X] T033 [US2] Update app route imports and dependency wiring for separate detail and status use cases in `app/api/routes.py`

**Checkpoint**: User Story 2 is functional when clients can poll status without receiving full command details.

---

## Phase 5: User Story 3 - List Commands by Status (Priority: P3)

**Goal**: Return paginated command summaries filtered by status.

**Independent Test**: Store commands with multiple statuses, list by `failed`, and verify only failed summaries are returned with `total`, `page`, and `page_size`.

### Tests for User Story 3

- [X] T034 [P] [US3] Add list use case tests for filtering commands by queued, processing, completed, and failed statuses in `tests/test_list_commands.py`
- [X] T035 [P] [US3] Add list use case tests for default pagination page 1 and page size 20 in `tests/test_list_commands.py`
- [X] T036 [P] [US3] Add list use case tests for explicit pagination and out-of-range pages in `tests/test_list_commands.py`
- [X] T037 [P] [US3] Add list use case tests for invalid status and invalid pagination errors in `tests/test_list_commands.py`
- [X] T038 [P] [US3] Add repository adapter tests for status-filtered listing in memory and Redis repositories in `tests/test_list_commands.py`
- [X] T039 [P] [US3] Add API tests for `GET /commands?status=failed&page=1&page_size=20` returning summaries only in `tests/test_api.py`
- [X] T040 [P] [US3] Add API tests for invalid status and invalid pagination returning HTTP 400 in `tests/test_api.py`
- [X] T041 [P] [US3] Add API read-only guard test proving list lookup does not enqueue, consume queue messages, or execute handlers in `tests/test_api.py`
- [X] T042 [P] [US3] Add OpenAPI documentation tests for list query parameters, summary items, pagination metadata, and errors in `tests/test_documentation.py`

### Implementation for User Story 3

- [X] T043 [US3] Create `ListCommands` request/result/errors and command summary mapping in `app/application/list_commands.py`
- [X] T044 [US3] Validate status filters against allowed command states in `app/application/list_commands.py`
- [X] T045 [US3] Validate page and page_size values and apply default page 1 and page size 20 in `app/application/list_commands.py`
- [X] T046 [US3] Add command summary and paginated command list response schemas in `app/api/schemas.py`
- [X] T047 [US3] Wire `ListCommands` into the FastAPI app state in `app/api/main.py`
- [X] T048 [US3] Add `GET /commands` route with status, page, and page_size query parameters in `app/api/routes.py`
- [X] T049 [US3] Map list use case validation errors to HTTP 400 responses in `app/api/routes.py`
- [X] T050 [US3] Add read-only success and validation logs for list queries without logging payloads in `app/api/routes.py`

**Checkpoint**: User Story 3 is functional when filtered paginated lists return only matching command summaries.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature, documentation, architecture constraints, and quickstart flow.

- [X] T051 [P] Update README with command detail, status-only, and list-by-status examples in `README.md`
- [X] T052 [P] Update documentation tests to reference the new README query examples in `tests/test_documentation.py`
- [X] T053 [P] Run the full pytest suite and fix regressions in `tests/`
- [X] T054 [P] Run focused query tests for API and use cases in `tests/test_api.py`, `tests/test_get_command.py`, `tests/test_get_command_status.py`, and `tests/test_list_commands.py`
- [X] T055 [P] Verify domain isolation checks still pass for query additions in `tests/test_architecture.py`
- [X] T056 Validate quickstart query flows against a running Docker Compose stack in `specs/005-command-query/quickstart.md`
- [X] T057 Review OpenAPI output to confirm query routes expose explicit contracts and do not expose Redis details in `app/api/routes.py`
- [X] T058 Update ADR or documentation notes if query behavior changes architectural decisions in `docs/adr/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2 and is the MVP.
- **Phase 4 US2**: Depends on Phase 2 and can be implemented after or alongside US1 once route conflicts are coordinated.
- **Phase 5 US3**: Depends on Phase 2 and repository list support.
- **Phase 6 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; no dependency on US2 or US3.
- **US2 (P2)**: Can start after Phase 2; route implementation should account for the existing `/commands/{id}` route from US1.
- **US3 (P3)**: Can start after Phase 2; depends on repository list primitives from foundational tasks.

### Within Each User Story

- Write or update tests before implementation tasks.
- Update application result contracts before API schemas.
- Update schemas before route response mapping.
- Verify each story's focused tests before moving to the next priority.

---

## Parallel Opportunities

- T005, T006, and T007 can run in parallel after setup.
- T011 through T016 can run in parallel as US1 tests.
- T023 through T028 can run in parallel as US2 tests.
- T034 through T042 can run in parallel as US3 tests.
- T051 through T055 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "T011 [P] [US1] Add full detail use case tests for queued, completed, failed, and processing records in tests/test_get_command.py"
Task: "T013 [P] [US1] Add API tests for GET /commands/{id} returning full details with id field and no command_id field in tests/test_api.py"
Task: "T016 [P] [US1] Add OpenAPI documentation tests for the full command detail response and error contracts in tests/test_documentation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T023 [P] [US2] Update status use case tests to assert status-only result includes exactly id and status in tests/test_get_command_status.py"
Task: "T025 [P] [US2] Add API tests for GET /commands/{id}/status across queued, processing, completed, and failed statuses in tests/test_api.py"
Task: "T028 [P] [US2] Add OpenAPI documentation tests for the status-only response and error contracts in tests/test_documentation.py"
```

## Parallel Example: User Story 3

```bash
Task: "T034 [P] [US3] Add list use case tests for filtering commands by queued, processing, completed, and failed statuses in tests/test_list_commands.py"
Task: "T039 [P] [US3] Add API tests for GET /commands?status=failed&page=1&page_size=20 returning summaries only in tests/test_api.py"
Task: "T042 [P] [US3] Add OpenAPI documentation tests for list query parameters, summary items, pagination metadata, and errors in tests/test_documentation.py"
```

---

## Implementation Strategy

### MVP First

Complete **Phase 3 / US1** first. It delivers the core command detail lookup and aligns `GET /commands/{id}` with the requested complete record contract.

### Incremental Delivery

1. Deliver US1 for full command detail lookup by id.
2. Deliver US2 for lightweight status polling without payload or response details.
3. Deliver US3 for status-filtered paginated monitoring lists.
4. Run polish tasks to validate documentation, architecture, OpenAPI, and quickstart behavior.

### Final Validation

The feature is complete when `pytest` passes, the query endpoints are read-only, list responses are paginated and filter correctly, and public docs describe all success and error contracts.
