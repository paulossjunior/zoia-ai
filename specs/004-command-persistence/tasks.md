# Tasks: Command Persistence

**Input**: Design documents from `/specs/004-command-persistence/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/command-persistence-contract.md`, `quickstart.md`

**Tests**: Tests are REQUIRED by the project constitution. Test tasks are listed before implementation tasks in each user story and cover success paths, validation, failure persistence, repository adapters, retrieval contracts, and proof that API submission remains asynchronous.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or has no dependency on incomplete tasks
- **[Story]**: User story label for story phases only
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current implementation baseline and align the feature workspace before changing behavior.

- [X] T001 Inspect the existing command lifecycle fields and methods in `app/domain/command.py`
- [X] T002 Inspect the existing submit, process, and retrieve use cases in `app/application/submit_command.py`, `app/application/process_command.py`, and `app/application/get_command_status.py`
- [X] T003 Inspect current Redis and in-memory repository serialization behavior in `app/infrastructure/redis_command_repository.py` and `app/infrastructure/memory_command_repository.py`
- [X] T004 Inspect current API schemas, route response models, and OpenAPI documentation in `app/api/schemas.py` and `app/api/routes.py`
- [X] T005 Run the current test suite to capture the pre-change baseline for `tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared naming, contract expectations, and architecture checks used by all user stories.

**CRITICAL**: No user story implementation should begin until these contract and baseline tests are in place.

- [X] T006 [P] Add reusable command record assertions for payload, response, error, and lifecycle timestamps in `tests/test_get_command_status.py`
- [X] T007 [P] Add architecture regression checks that domain modules do not import FastAPI, Redis, Docker, or infrastructure modules in `tests/test_documentation.py`
- [X] T008 [P] Add persisted command record contract examples for queued, completed, and failed records in `tests/test_documentation.py`
- [X] T009 Define the canonical internal-to-external timestamp mapping expectations in `tests/test_get_command_status.py`
- [X] T010 Update documentation tests to require the complete persisted command record contract in `tests/test_documentation.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Persist Submitted Command Before Queueing (Priority: P1) MVP

**Goal**: Persist every accepted command before queue publication with id, type, original payload, queued status, and request receipt timestamp.

**Independent Test**: Submit a valid command through the use case or API, verify the record exists before queue publication, and confirm invalid submissions create no record and queue no message.

### Tests for User Story 1

- [X] T011 [P] [US1] Add SubmitCommand test proving repository save happens before queue enqueue in `tests/test_submit_command.py`
- [X] T012 [P] [US1] Add SubmitCommand test proving original payload is persisted unchanged with queued status in `tests/test_submit_command.py`
- [X] T013 [P] [US1] Add SubmitCommand test proving request receipt timestamp is set on accepted commands in `tests/test_submit_command.py`
- [X] T014 [P] [US1] Add SubmitCommand validation test proving invalid commands are neither persisted nor queued in `tests/test_submit_command.py`
- [X] T015 [P] [US1] Add API test proving `POST /commands` persists a retrievable queued record without executing processing in `tests/test_api.py`
- [X] T016 [P] [US1] Add Redis repository serialization test for queued command payload and request receipt timestamp in `tests/test_get_command_status.py`

### Implementation for User Story 1

- [X] T017 [US1] Extend `Command` with `response`, `request_received_at`, `processing_started_at`, and `processing_finished_at` fields while preserving compatibility aliases in `app/domain/command.py`
- [X] T018 [US1] Update `Command` construction defaults so accepted commands start with queued status, original payload, null response, null error, and request receipt timestamp in `app/domain/command.py`
- [X] T019 [US1] Update SubmitCommand to persist the complete queued command record before enqueueing in `app/application/submit_command.py`
- [X] T020 [US1] Update SubmitCommand logging to include command id, type, queued status, and persistence-before-enqueue lifecycle in `app/application/submit_command.py`
- [X] T021 [US1] Update RedisCommandRepository serialization to write the complete queued record fields using contract names in `app/infrastructure/redis_command_repository.py`
- [X] T022 [US1] Update RedisCommandRepository deserialization to read contract names and existing legacy timestamp keys safely in `app/infrastructure/redis_command_repository.py`
- [X] T023 [US1] Update MemoryCommandRepository behavior or tests support so payload and receipt timestamp remain available after save and get in `app/infrastructure/memory_command_repository.py`

**Checkpoint**: User Story 1 is functional when a valid submission is persisted before enqueue and invalid input leaves storage and queue unchanged.

---

## Phase 4: User Story 2 - Persist Processing Outcome and Execution History (Priority: P2)

**Goal**: Persist processing start time, finish time, success response, failure error, and final status while preserving the original payload.

**Independent Test**: Process successful and failing commands, retrieve each record, and verify status transitions, timestamps, response or error, and payload retention.

### Tests for User Story 2

- [X] T024 [P] [US2] Add ProcessCommand success test proving status becomes processing before pipeline execution in `tests/test_process_command.py`
- [X] T025 [P] [US2] Add ProcessCommand success test proving completed status, finish timestamp, and context result response are persisted in `tests/test_process_command.py`
- [X] T026 [P] [US2] Add ProcessCommand failure test proving failed status, finish timestamp, error message, and null response are persisted in `tests/test_process_command.py`
- [X] T027 [P] [US2] Add no-pipeline failure test proving missing handler registry entry persists a clear failed record in `tests/test_process_command.py`
- [X] T028 [P] [US2] Add payload retention test proving status and outcome updates do not mutate original payload in `tests/test_process_command.py`
- [X] T029 [P] [US2] Add worker test proving consumed commands end with persisted completed or failed records in `tests/test_worker.py`
- [X] T030 [P] [US2] Add Chain of Responsibility test proving handler-produced context result is available for persistence after pipeline success in `tests/test_chain_of_responsibility.py`

### Implementation for User Story 2

- [X] T031 [US2] Update `Command.mark_processing` to set processing start timestamp, clear stale processing outcome fields, and preserve payload in `app/domain/command.py`
- [X] T032 [US2] Update `Command.mark_completed` to accept optional response, set processing finish timestamp, clear error message, and preserve payload in `app/domain/command.py`
- [X] T033 [US2] Update `Command.mark_failed` to set processing finish timestamp, persist clear error message, clear response, and preserve payload in `app/domain/command.py`
- [X] T034 [US2] Update ProcessCommand to persist processing status before pipeline execution in `app/application/process_command.py`
- [X] T035 [US2] Update ProcessCommand to persist `CommandContext.result` as command response on successful pipeline execution in `app/application/process_command.py`
- [X] T036 [US2] Update ProcessCommand to persist failed status and clear error messages for pipeline resolution and handler exceptions in `app/application/process_command.py`
- [X] T037 [US2] Update application logging for processing start, completion, and failure with command id and type in `app/application/process_command.py`
- [X] T038 [US2] Update TestCommand business handler to produce the documented echo response in `app/commands/test_command/handlers.py`
- [X] T039 [US2] Update RedisCommandRepository full-record updates so response, error, timestamps, type, and payload stay tied to the same id in `app/infrastructure/redis_command_repository.py`

**Checkpoint**: User Story 2 is functional when worker processing leaves a durable completed or failed command record with the expected outcome details.

---

## Phase 5: User Story 3 - Retrieve Complete Command Execution Record (Priority: P3)

**Goal**: Retrieve a complete command execution record by id, including current status, original payload, response, error, and lifecycle timestamps.

**Independent Test**: Retrieve queued, completed, failed, and unknown command ids through the public API and verify the response contract.

### Tests for User Story 3

- [X] T040 [P] [US3] Add GET `/commands/{command_id}` API test for queued record with payload and request receipt timestamp in `tests/test_api.py`
- [X] T041 [P] [US3] Add GET `/commands/{command_id}` API test for completed record with response and null error in `tests/test_api.py`
- [X] T042 [P] [US3] Add GET `/commands/{command_id}` API test for failed record with error message and null response in `tests/test_api.py`
- [X] T043 [P] [US3] Add GET `/commands/{command_id}` API test for unknown command returning 404 in `tests/test_api.py`
- [X] T044 [P] [US3] Add use case test proving retrieved records include all complete execution fields in `tests/test_get_command_status.py`
- [X] T045 [P] [US3] Add OpenAPI documentation test proving retrieval schema documents payload, response, error, and lifecycle timestamps in `tests/test_documentation.py`

### Implementation for User Story 3

- [X] T046 [US3] Extend the command retrieval result object with payload, response, request receipt time, processing start time, and processing finish time in `app/application/get_command_status.py`
- [X] T047 [US3] Add or update the complete execution record response schema in `app/api/schemas.py`
- [X] T048 [US3] Update `GET /commands/{command_id}` to return the complete persisted execution record contract in `app/api/routes.py`
- [X] T049 [US3] Update route examples and error documentation for complete command retrieval in `app/api/routes.py`
- [X] T050 [US3] Update API serialization to expose contract timestamp names while preserving internal compatibility fields in `app/api/schemas.py`
- [X] T051 [US3] Update README command retrieval examples to show payload, response, error, and lifecycle timestamps in `README.md`

**Checkpoint**: User Story 3 is functional when one retrieval operation shows the command's current state and complete persisted execution record.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature, documentation, architecture constraints, and local Docker workflow.

- [X] T052 [P] Run the full pytest suite and fix regressions in `tests/`
- [X] T053 [P] Run focused API and processing tests for command persistence in `tests/test_api.py`, `tests/test_submit_command.py`, `tests/test_process_command.py`, and `tests/test_get_command_status.py`
- [X] T054 [P] Verify domain isolation checks still pass and no domain module imports infrastructure or web framework code in `app/domain/`
- [X] T055 Validate the quickstart flow with Docker Compose API, worker, Redis, and RedisInsight in `docker-compose.yml`
- [X] T056 Validate RedisInsight documentation still matches local compose access in `README.md`
- [X] T057 Review command persistence observability logs for submission, processing start, success, and failure in `app/application/submit_command.py` and `app/application/process_command.py`
- [X] T058 Update feature quickstart notes with any final command examples or response shape adjustments in `specs/004-command-persistence/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2 and is the MVP.
- **Phase 4 US2**: Depends on Phase 2, and uses the persisted record created by US1.
- **Phase 5 US3**: Depends on Phase 2, and is most valuable after US1/US2 records exist.
- **Phase 6 Polish**: Depends on the selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2; no dependency on US2 or US3.
- **US2 (P2)**: Can start after Phase 2, but final verification depends on persisted records from US1.
- **US3 (P3)**: Can start after Phase 2, but full success/completed/failed examples depend on US1 and US2.

### Within Each User Story

- Write or update tests before implementation tasks.
- Update domain model before application use cases.
- Update application use cases before API route serialization.
- Update repository serialization before Docker or quickstart validation.
- Each story should pass its focused tests before moving to the next priority.

---

## Parallel Opportunities

- T006, T007, T008, T009, and T010 can run in parallel after setup because they touch independent test concerns.
- T011 through T016 can run in parallel as US1 tests.
- T024 through T030 can run in parallel as US2 tests.
- T040 through T045 can run in parallel as US3 tests.
- T052, T053, T054, and T056 can run in parallel after implementation because they validate different files or workflows.

---

## Parallel Example: User Story 1

```bash
# Tests that can be prepared together:
Task: "T011 [P] [US1] Add SubmitCommand test proving repository save happens before queue enqueue in tests/test_submit_command.py"
Task: "T015 [P] [US1] Add API test proving POST /commands persists a retrievable queued record without executing processing in tests/test_api.py"
Task: "T016 [P] [US1] Add Redis repository serialization test for queued command payload and request receipt timestamp in tests/test_get_command_status.py"
```

## Parallel Example: User Story 2

```bash
# Tests that can be prepared together:
Task: "T025 [P] [US2] Add ProcessCommand success test proving completed status, finish timestamp, and context result response are persisted in tests/test_process_command.py"
Task: "T026 [P] [US2] Add ProcessCommand failure test proving failed status, finish timestamp, error message, and null response are persisted in tests/test_process_command.py"
Task: "T029 [P] [US2] Add worker test proving consumed commands end with persisted completed or failed records in tests/test_worker.py"
```

## Parallel Example: User Story 3

```bash
# Tests that can be prepared together:
Task: "T040 [P] [US3] Add GET /commands/{command_id} API test for queued record with payload and request receipt timestamp in tests/test_api.py"
Task: "T041 [P] [US3] Add GET /commands/{command_id} API test for completed record with response and null error in tests/test_api.py"
Task: "T045 [P] [US3] Add OpenAPI documentation test proving retrieval schema documents payload, response, error, and lifecycle timestamps in tests/test_documentation.py"
```

---

## Implementation Strategy

### MVP First

Complete **Phase 3 / US1** first. It delivers the essential guarantee that accepted commands are persisted before queue publication and remain retrievable as queued records.

### Incremental Delivery

1. Deliver US1 and verify accepted commands have durable queued records.
2. Deliver US2 and verify worker outcome persistence for completed and failed processing.
3. Deliver US3 and verify the public retrieval contract returns the complete execution record.
4. Run Polish tasks to validate tests, Docker Compose, RedisInsight documentation, and observability.

### Final Validation

The feature is complete when `pytest` passes, Docker Compose supports the submit/process/retrieve flow, Redis stores the full command record, and `GET /commands/{command_id}` returns the complete persisted execution record.
