# Tasks: Command Status Query

**Input**: Design documents from `/specs/003-command-status-query/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/command-status-contract.md`, `quickstart.md`

**Tests**: Required by the project constitution. Tests must cover successful status lookup, validation errors, not-found errors, read-only behavior, no queue/handler execution, and generated documentation.

**Organization**: Tasks are grouped by user story to allow independent implementation and validation.

## Phase 1: Setup (Shared Test Harness)

**Purpose**: Prepare the feature without changing runtime behavior.

- [X] T001 Inspect existing command submission route and dependency wiring in `app/api/routes.py`
- [X] T002 [P] Inspect existing command repository usage and serialization behavior in `app/infrastructure/redis_command_repository.py`
- [X] T003 [P] Inspect existing API/documentation tests for reusable helpers in `tests/test_documentation.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared response examples, validation rules, and read-only use case boundary.

**CRITICAL**: Complete this phase before starting any user story implementation.

- [X] T004 Define canonical command status success and error examples in `tests/test_get_command_status.py`
- [X] T005 Define fake queue/handler guards proving status lookup is read-only in `tests/test_api.py`
- [X] T006 Create the read-only application use case module shell in `app/application/get_command_status.py`
- [X] T007 Add shared status response and lookup error schema names to documentation expectations in `tests/test_documentation.py`

**Checkpoint**: Shared test fixtures and the application use case boundary are ready.

---

## Phase 3: User Story 1 - Check Submitted Command Status (Priority: P1) MVP

**Goal**: Clients can query a known command id and see current lifecycle status, type, timestamps, and failure reason without seeing the payload.

**Independent Test**: Create commands in the repository with queued, processing, completed, and failed states, then query their ids and verify the response body reflects each state.

### Tests for User Story 1

- [X] T008 [P] [US1] Add use case test for queued command status view in `tests/test_get_command_status.py`
- [X] T009 [P] [US1] Add use case test for processing command status view in `tests/test_get_command_status.py`
- [X] T010 [P] [US1] Add use case test for completed command status view in `tests/test_get_command_status.py`
- [X] T011 [P] [US1] Add use case test for failed command status view with `error_message` in `tests/test_get_command_status.py`
- [X] T012 [P] [US1] Add API integration test for `GET /commands/{command_id}` returning `200` for a known command in `tests/test_api.py`
- [X] T013 [P] [US1] Add API test that status response does not include original payload in `tests/test_api.py`
- [X] T014 [P] [US1] Add API test that status lookup does not publish to queue or execute command handlers in `tests/test_api.py`

### Implementation for User Story 1

- [X] T015 [US1] Implement `GetCommandStatusRequest`, `GetCommandStatusResult`, and success mapping in `app/application/get_command_status.py`
- [X] T016 [US1] Add `CommandStatusResponse` schema with datetime fields and no payload field in `app/api/schemas.py`
- [X] T017 [US1] Wire `GetCommandStatus` into app state during app creation in `app/api/main.py`
- [X] T018 [US1] Implement `GET /commands/{command_id}` success path in `app/api/routes.py`
- [X] T019 [US1] Add status lookup success logging without status mutation in `app/api/routes.py`

**Checkpoint**: User Story 1 can be validated independently by querying stored commands through the API.

---

## Phase 4: User Story 2 - Handle Unknown or Invalid Command Identifiers (Priority: P2)

**Goal**: Clients receive clear errors for malformed ids and unknown commands.

**Independent Test**: Query `not-a-uuid` and a valid UUID with no stored command, then verify `400 invalid command_id` and `404 command not found`.

### Tests for User Story 2

- [X] T020 [P] [US2] Add use case test that malformed command ids are rejected before repository lookup in `tests/test_get_command_status.py`
- [X] T021 [P] [US2] Add use case test that unknown valid command ids raise a controlled not-found error in `tests/test_get_command_status.py`
- [X] T022 [P] [US2] Add API test that malformed command id returns HTTP 400 with `invalid command_id` in `tests/test_api.py`
- [X] T023 [P] [US2] Add API test that unknown valid command id returns HTTP 404 with `command not found` in `tests/test_api.py`
- [X] T024 [P] [US2] Add API test that error bodies do not expose repository, Redis, storage, or queue details in `tests/test_api.py`

### Implementation for User Story 2

- [X] T025 [US2] Add `InvalidCommandIdError` and `CommandStatusNotFoundError` to `app/application/get_command_status.py`
- [X] T026 [US2] Validate UUID command id before repository lookup in `app/application/get_command_status.py`
- [X] T027 [US2] Add HTTP exception handlers or route handling for `400` and `404` status lookup errors in `app/api/routes.py`
- [X] T028 [US2] Add `ErrorResponse` examples for invalid id and not found in `app/api/schemas.py`
- [X] T029 [US2] Add validation failure and not-found logging in `app/api/routes.py`

**Checkpoint**: User Story 2 can be validated independently through error responses.

---

## Phase 5: User Story 3 - Discover Status Query Contract (Priority: P3)

**Goal**: Developers and testers can discover and validate the status query through API docs and README instructions.

**Independent Test**: Inspect `/openapi.json`, `/docs`, and README to confirm `GET /commands/{command_id}` includes success, `400`, and `404` examples matching runtime behavior.

### Tests for User Story 3

- [X] T030 [P] [US3] Add documentation test that OpenAPI includes `GET /commands/{command_id}` with summary, description, and commands tag in `tests/test_documentation.py`
- [X] T031 [P] [US3] Add documentation test that OpenAPI success schema includes all status view fields and excludes `payload` in `tests/test_documentation.py`
- [X] T032 [P] [US3] Add documentation test that OpenAPI documents `400 invalid command_id` example in `tests/test_documentation.py`
- [X] T033 [P] [US3] Add documentation test that OpenAPI documents `404 command not found` example in `tests/test_documentation.py`
- [X] T034 [P] [US3] Add README test for status query curl example and expected statuses in `tests/test_documentation.py`

### Implementation for User Story 3

- [X] T035 [US3] Add OpenAPI metadata, path parameter docs, and response examples to `GET /commands/{command_id}` in `app/api/routes.py`
- [X] T036 [US3] Add schema descriptions and examples for `CommandStatusResponse` in `app/api/schemas.py`
- [X] T037 [US3] Update README with status query instructions, success example, and invalid/not-found examples in `README.md`
- [X] T038 [US3] Update README to state status lookup is read-only and does not require queue/storage knowledge in `README.md`

**Checkpoint**: User Story 3 can be validated through generated docs and README without reading source code.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate integration, architecture, and quickstart behavior end to end.

- [X] T039 [P] Add architecture test ensuring domain layer remains free of status query infrastructure dependencies in `tests/test_architecture.py`
- [X] T040 [P] Add documentation/source inspection for the new use case module in `tests/test_documentation.py`
- [X] T041 Run focused status query tests and fix failures in `tests/test_get_command_status.py`
- [X] T042 Run API and documentation tests and fix failures in `tests/test_api.py`
- [X] T043 Run the full pytest suite and address regressions in `tests/test_get_command_status.py`
- [X] T044 Validate Docker Compose quickstart for submit-then-query flow and update notes in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 (Phase 3)**: Depends on Foundational and is the MVP.
- **US2 (Phase 4)**: Depends on Foundational; can be implemented after or alongside US1 error-independent pieces.
- **US3 (Phase 5)**: Depends on route/schema names from US1 and US2.
- **Polish (Phase 6)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3.
- **US2 (P2)**: Reuses the use case and route introduced for US1.
- **US3 (P3)**: Depends on finalized runtime response shapes from US1 and US2.

### Within Each User Story

- Tests must be written before or alongside implementation.
- Application use case behavior comes before route integration.
- Route behavior comes before documentation examples.
- Each story must pass its independent test before progressing.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001.
- T008-T014 can run in parallel because they add separate assertions.
- T020-T024 can run in parallel because they cover independent error cases.
- T030-T034 can run in parallel once route/schema names are known.
- T039 and T040 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "T008 [US1] Add queued command use case test in tests/test_get_command_status.py"
Task: "T010 [US1] Add completed command use case test in tests/test_get_command_status.py"
Task: "T012 [US1] Add API 200 status lookup test in tests/test_api.py"
Task: "T014 [US1] Add read-only API behavior test in tests/test_api.py"
```

## Parallel Example: User Story 2

```bash
Task: "T020 [US2] Add malformed id use case test in tests/test_get_command_status.py"
Task: "T021 [US2] Add unknown id use case test in tests/test_get_command_status.py"
Task: "T022 [US2] Add API 400 test in tests/test_api.py"
Task: "T023 [US2] Add API 404 test in tests/test_api.py"
```

## Parallel Example: User Story 3

```bash
Task: "T030 [US3] Add OpenAPI operation test in tests/test_documentation.py"
Task: "T032 [US3] Add OpenAPI 400 example test in tests/test_documentation.py"
Task: "T034 [US3] Add README status query test in tests/test_documentation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Add use case and API tests for known command lookup.
3. Implement the read-only use case and `GET /commands/{command_id}` success path.
4. Validate that a known command returns lifecycle status and no payload.

### Incremental Delivery

1. Deliver US1 for successful status visibility.
2. Deliver US2 for reliable invalid/not-found errors.
3. Deliver US3 for OpenAPI and README discoverability.
4. Complete polish tasks and full validation.

### Validation Commands

```bash
pytest tests/test_get_command_status.py
pytest tests/test_api.py tests/test_documentation.py
pytest
docker compose up --build
```

## Notes

- `[P]` tasks touch independent files or independent assertions.
- `[US#]` labels map tasks to prioritized user stories.
- Status lookup is read-only: no queue publication, no queue consumption, no handler execution, no status mutation.
- Public status responses must not include command payload.
