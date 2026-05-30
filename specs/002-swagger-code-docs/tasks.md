# Tasks: Swagger and Code Documentation

**Input**: Design documents from `/specs/002-swagger-code-docs/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/documentation-contract.md`, `quickstart.md`

**Tests**: Required by the project constitution. Documentation regressions must be caught by pytest through FastAPI schema checks, source documentation checks, README checks, and architecture boundary checks.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Documentation Test Harness)

**Purpose**: Prepare the documentation validation surface without changing runtime behavior.

- [X] T001 Inspect current FastAPI app, route, schema, README, and command-processing module documentation gaps in `app/api/main.py`
- [X] T002 [P] Create documentation test module placeholder and shared constants for docs URLs/examples in `tests/test_documentation.py`
- [X] T003 [P] Inspect existing architecture tests and identify reusable domain-boundary assertions in `tests/test_architecture.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared examples and documentation expectations used by all user stories.

**CRITICAL**: No user story work should begin until these expectations are represented in tests or constants.

- [X] T004 Define canonical `TEST_COMMAND` request and queued acknowledgement examples in `tests/test_documentation.py`
- [X] T005 Define list of public command-processing modules that require concise documentation in `tests/test_documentation.py`
- [X] T006 Define external API documentation forbidden terms that would leak queue implementation requirements in `tests/test_documentation.py`

**Checkpoint**: Documentation targets and examples are explicit and ready for story work.

---

## Phase 3: User Story 1 - Explore Command API Documentation (Priority: P1) MVP

**Goal**: External integrators can open interactive API docs and understand `POST /commands`, required fields, success acknowledgement, validation errors, and a valid example.

**Independent Test**: Start or instantiate the API, fetch `/docs` and `/openapi.json`, and confirm `POST /commands` documents the request body, `202` response, `400` response, and valid example matching endpoint behavior.

### Tests for User Story 1

- [X] T007 [P] [US1] Add test that `/docs` returns HTTP 200 and exposes the interactive docs page in `tests/test_documentation.py`
- [X] T008 [P] [US1] Add test that `/openapi.json` includes `POST /commands` with operation summary, description, and tag in `tests/test_documentation.py`
- [X] T009 [P] [US1] Add test that command request schema marks `type` and `payload` as required and describes both fields in `tests/test_documentation.py`
- [X] T010 [P] [US1] Add test that `POST /commands` documents `202` acknowledgement containing `command_id` and `status` in `tests/test_documentation.py`
- [X] T011 [P] [US1] Add test that `POST /commands` documents `400` validation error response with an example body in `tests/test_documentation.py`
- [X] T012 [P] [US1] Add test that documented `TEST_COMMAND` example is accepted by the real endpoint with status `202` in `tests/test_documentation.py`
- [X] T013 [P] [US1] Add test that public OpenAPI text for `POST /commands` does not require clients to know Redis or queue internals in `tests/test_documentation.py`

### Implementation for User Story 1

- [X] T014 [US1] Configure FastAPI title, description, version, docs URL, OpenAPI URL, and tag metadata in `app/api/main.py`
- [X] T015 [US1] Add Pydantic field descriptions, required-field examples, and model examples for command submission and acknowledgement in `app/api/schemas.py`
- [X] T016 [US1] Add `POST /commands` summary, description, tags, status code metadata, and response documentation in `app/api/routes.py`
- [X] T017 [US1] Add documented `202` response example for queued acknowledgement in `app/api/routes.py`
- [X] T018 [US1] Add documented `400` response example for invalid command submissions in `app/api/routes.py`
- [X] T019 [US1] Align API validation error behavior and documented error shape for missing `type`, missing `payload`, and non-object `payload` in `app/api/main.py`

**Checkpoint**: User Story 1 is independently testable through `/docs`, `/openapi.json`, and `POST /commands`.

---

## Phase 4: User Story 2 - Understand Command Processing Code (Priority: P2)

**Goal**: Developers can read concise documentation at the domain, application, infrastructure, API, worker, registry, and pipeline boundaries and understand how to extend command processing safely.

**Independent Test**: Run documentation/source inspection tests and confirm public command-processing modules include concise responsibility or extension-point documentation without introducing domain dependencies on FastAPI, Redis, Docker, or infrastructure.

### Tests for User Story 2

- [X] T020 [P] [US2] Add test that required command-processing modules contain module docstrings in `tests/test_documentation.py`
- [X] T021 [P] [US2] Add test that key public classes and functions contain concise docstrings in `tests/test_documentation.py`
- [X] T022 [P] [US2] Add test that handler registry and pipeline docs explain adding a command type without changing worker flow in `tests/test_documentation.py`
- [X] T023 [P] [US2] Add architecture test that domain documentation and imports remain free of FastAPI, Redis, Docker, and infrastructure coupling in `tests/test_architecture.py`

### Implementation for User Story 2

- [X] T024 [P] [US2] Add concise lifecycle and invariant documentation to command entity in `app/domain/command.py`
- [X] T025 [P] [US2] Add concise status-transition documentation to command status enum in `app/domain/status.py`
- [X] T026 [P] [US2] Add shared handler-context documentation to `app/domain/context.py`
- [X] T027 [P] [US2] Add port/interface responsibility documentation to `app/domain/ports.py`
- [X] T028 [P] [US2] Add base handler responsibility and chain behavior documentation to `app/domain/handlers.py`
- [X] T029 [P] [US2] Add submission boundary documentation to `app/application/submit_command.py`
- [X] T030 [P] [US2] Add worker-processing lifecycle and failure documentation to `app/application/process_command.py`
- [X] T031 [P] [US2] Add registry extension and missing-pipeline behavior documentation to `app/application/handler_registry.py`
- [X] T032 [P] [US2] Add sequential pipeline and interruption behavior documentation to `app/application/pipelines.py`
- [X] T033 [P] [US2] Add queue adapter responsibility documentation without leaking it into the domain in `app/infrastructure/redis_queue.py`
- [X] T034 [P] [US2] Add repository adapter responsibility documentation to `app/infrastructure/redis_command_repository.py`
- [X] T035 [P] [US2] Add test/local repository responsibility documentation to `app/infrastructure/memory_command_repository.py`
- [X] T036 [P] [US2] Add logging configuration responsibility documentation to `app/infrastructure/logging.py`
- [X] T037 [P] [US2] Add API boundary documentation to `app/api/routes.py`
- [X] T038 [P] [US2] Add worker loop and single-iteration documentation to `app/worker/main.py`
- [X] T039 [P] [US2] Add `TEST_COMMAND` handler responsibility documentation to `app/commands/test_command/handlers.py`
- [X] T040 [P] [US2] Add `TEST_COMMAND` pipeline extension-pattern documentation to `app/commands/test_command/pipeline.py`

**Checkpoint**: User Story 2 is independently testable through docstring and architecture tests.

---

## Phase 5: User Story 3 - Use Documentation During Local Validation (Priority: P3)

**Goal**: Developers and testers can use the README to start the service, open API docs, submit the documented example, run documentation tests, and understand extension documentation expectations.

**Independent Test**: Follow README instructions to locate `/docs`, submit the documented `TEST_COMMAND` request, run pytest, and identify the documented steps for adding a command type.

### Tests for User Story 3

- [X] T041 [P] [US3] Add README test that local API docs URL `http://localhost:8000/docs` is documented in `tests/test_documentation.py`
- [X] T042 [P] [US3] Add README test that the documented curl example matches the OpenAPI `TEST_COMMAND` example in `tests/test_documentation.py`
- [X] T043 [P] [US3] Add README test that new command type guidance names pipeline, handlers, registry, and payload contract updates in `tests/test_documentation.py`
- [X] T044 [P] [US3] Add README test that external clients are not required to know Redis or queue implementation details in `tests/test_documentation.py`

### Implementation for User Story 3

- [X] T045 [US3] Add local Swagger/OpenAPI docs instructions and URL to `README.md`
- [X] T046 [US3] Add documented `TEST_COMMAND` curl example and expected `202` acknowledgement to `README.md`
- [X] T047 [US3] Add documentation validation instructions for `pytest` and `/openapi.json` checks to `README.md`
- [X] T048 [US3] Add concise extension guide for new command types and required documentation updates to `README.md`
- [X] T049 [US3] Add external-client note that queue implementation details are internal and replaceable in `README.md`

**Checkpoint**: User Story 3 is independently testable through README inspection and local validation steps.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the generated documentation, README, tests, and architecture rules all remain aligned.

- [X] T050 [P] Run focused API and documentation tests and fix any failures in `tests/test_documentation.py`
- [X] T051 [P] Run architecture tests and fix any boundary documentation/import failures in `tests/test_architecture.py`
- [X] T052 Run full pytest suite and update any stale documentation assertions in `tests/test_documentation.py`
- [X] T053 Validate Docker Compose quickstart reaches `/docs` and document any command changes in `README.md`
- [X] T054 Review all new comments/docstrings for concision and remove redundant narration in `app/domain/command.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and can run independently from US1 after shared expectations exist.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US1 examples and US2 extension wording.
- **Polish (Phase 6)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3.
- **US2 (P2)**: No dependency on US1 runtime changes, but should reuse the same terminology.
- **US3 (P3)**: Should align with US1 OpenAPI examples and US2 extension docs.

### Within Each User Story

- Write tests before or alongside implementation.
- Keep API documentation changes aligned with actual Pydantic/FastAPI behavior.
- Keep code documentation concise and focused on responsibility, invariants, and extension points.
- Validate each story independently before moving to the next priority.

### Parallel Opportunities

- Setup tasks T002 and T003 can run in parallel.
- Foundational tasks T004-T006 can run in parallel after T001.
- US1 tests T007-T013 can run in parallel before API documentation implementation.
- US2 documentation tasks T024-T040 touch different files and can run in parallel after tests T020-T023 define expectations.
- US3 tests T041-T044 can run in parallel before README edits T045-T049.

---

## Parallel Example: User Story 1

```bash
# Parallelizable test work:
Task: "T008 [US1] Add OpenAPI operation test in tests/test_documentation.py"
Task: "T010 [US1] Add 202 response documentation test in tests/test_documentation.py"
Task: "T011 [US1] Add 400 response documentation test in tests/test_documentation.py"

# Then implement route/schema metadata:
Task: "T015 [US1] Add schema descriptions and examples in app/api/schemas.py"
Task: "T016 [US1] Add route summary, description, tags, and responses in app/api/routes.py"
```

## Parallel Example: User Story 2

```bash
Task: "T024 [US2] Document app/domain/command.py"
Task: "T029 [US2] Document app/application/submit_command.py"
Task: "T033 [US2] Document app/infrastructure/redis_queue.py"
Task: "T038 [US2] Document app/worker/main.py"
```

## Parallel Example: User Story 3

```bash
Task: "T041 [US3] Add README docs URL test in tests/test_documentation.py"
Task: "T043 [US3] Add README extension guidance test in tests/test_documentation.py"
Task: "T045 [US3] Add local docs instructions to README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests T007-T013.
3. Complete US1 implementation T014-T019.
4. Validate `/docs`, `/openapi.json`, and the documented `POST /commands` example.

### Incremental Delivery

1. Deliver US1 so external API docs are usable.
2. Deliver US2 so maintainers have boundary and extension documentation.
3. Deliver US3 so README-driven local validation includes documentation quality.
4. Run Phase 6 to confirm all docs, tests, and quickstart instructions agree.

### Validation Commands

```bash
pytest tests/test_documentation.py
pytest tests/test_architecture.py
pytest
docker compose up --build
```

## Notes

- `[P]` tasks touch different files or independent assertions and can run in parallel.
- `[US#]` labels map tasks to the user story they deliver.
- Avoid verbose comments that merely restate code.
- Public API docs should describe external command submission behavior, not Redis or storage internals.
