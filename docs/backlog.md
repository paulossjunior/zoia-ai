# Project Backlog

This backlog consolidates the implemented Spec Kit features in `specs/` into a
product delivery view. Each spec directory maps to one epic. User stories and
task groups are traceable to the corresponding `spec.md` and `tasks.md` files.

## Status Legend

- **Done**: all tasks in the source `tasks.md` are checked.
- **Priority**: copied from the source user story priority.
- **Task IDs**: refer to the task identifiers in the source spec directory.

## Backlog Summary

| Epic | Source | Status | User Stories | Tasks |
|------|--------|--------|--------------|-------|
| EPIC-001 Async Command Processing | `specs/001-async-command-processing` | Done | 5 | 81 |
| EPIC-002 Swagger and Code Documentation | `specs/002-swagger-code-docs` | Done | 3 | 54 |
| EPIC-003 Command Status Query | `specs/003-command-status-query` | Done | 3 | 44 |
| EPIC-004 Command Persistence | `specs/004-command-persistence` | Done | 3 | 58 |
| EPIC-005 Command Query | `specs/005-command-query` | Done | 3 | 58 |
| EPIC-006 Command Callback Persistence | `specs/006-command-callback-persistence` | Done | 4 | 96 |

---

## EPIC-001: Async Command Processing

**Source**: `specs/001-async-command-processing`  
**Status**: Done  
**Goal**: Implement the first asynchronous command-processing service with
FastAPI, Redis queueing, separate worker execution, Chain of Responsibility
pipelines, Docker Compose, and automated tests.

### US-001.1: Submit Valid Command

**Priority**: P1  
**Status**: Done  
**Outcome**: External systems can submit valid commands through `POST /commands`
and receive an immediate queued acknowledgement.

Tasks:

- T001-T009: Create Python project structure, package markers, dependencies, and pytest fixtures.
- T010-T011: Define command status and command entity basics.
- T015-T016: Define repository and queue ports.
- T020-T022: Implement `SubmitCommand` validation, UUID creation, persistence, queue publication, and result contract.
- T038, T040, T043: Implement in-memory repository, Redis queue publication, and logging setup.
- T044, T046, T048-T049: Implement API schemas, `POST /commands`, dependency wiring, and submission logs.
- T060, T062-T063, T074: Test valid submission, no handler execution in API, persistence before queueing, and domain isolation.
- T076-T079: Document project purpose, setup, Docker startup, and command submission examples.

### US-001.2: Reject Invalid Command

**Priority**: P1  
**Status**: Done  
**Outcome**: Invalid command envelopes are rejected with HTTP 400 and are not
persisted or queued.

Tasks:

- T021: Validate non-empty `type` and object `payload` in the submit use case.
- T045, T047: Add strict Pydantic validation and map validation failures to HTTP 400.
- T061, T064: Test invalid API payloads and invalid use-case envelopes.

### US-001.3: Process Queued Command

**Priority**: P2  
**Status**: Done  
**Outcome**: A worker consumes queued command ids, resolves the correct pipeline,
and updates commands through `processing` and `completed`.

Tasks:

- T012-T013: Add command lifecycle and command context support.
- T017-T018: Define handler and pipeline ports.
- T023-T025: Implement `ProcessCommand` lookup, processing transition, and completed transition.
- T027, T029-T033: Implement ordered Chain of Responsibility and `TEST_COMMAND` handlers.
- T034: Implement `HandlerRegistry`.
- T039, T041: Configure Redis queue consumption.
- T050-T052, T054: Implement worker dependency factory, single-iteration processing, continuous loop, and type-agnostic worker flow.
- T065, T068-T070, T072: Test process success, worker consumption, Redis queue serialization, handler order, and shared context.

### US-001.4: Record Processing Failure

**Priority**: P2  
**Status**: Done  
**Outcome**: Missing pipelines, handler exceptions, invalid payloads, and other
processing failures produce traceable failed commands.

Tasks:

- T014: Ensure failed commands record safe error messages and completion timestamps.
- T026: Persist failed status for missing commands, missing pipelines, context errors, and handler exceptions.
- T028: Stop pipeline execution when context contains blocking errors.
- T035, T042, T053: Add controlled unknown-pipeline errors, safe queue decode handling, and worker failure logs.
- T066-T067, T071: Test unknown command types, handler exceptions, and validation interruption.

### US-001.5: Add New Command Handler

**Priority**: P3  
**Status**: Done  
**Outcome**: New command types can be added with new pipelines and registry
entries without changing the worker flow.

Tasks:

- T036-T037: Register `TEST_COMMAND` through the default registry and document extension behavior.
- T073: Test new command type execution without worker changes.
- T081: Document how to add new command types through handlers, pipelines, and registry entries.

---

## EPIC-002: Swagger and Code Documentation

**Source**: `specs/002-swagger-code-docs`  
**Status**: Done  
**Goal**: Add explicit API documentation, Swagger/OpenAPI metadata, code
docstrings, and documentation validation tests.

### US-002.1: Explore Command API Documentation

**Priority**: P1  
**Status**: Done  
**Outcome**: Developers can inspect command submission contracts through
Swagger UI and OpenAPI.

Tasks:

- T001-T006: Inspect documentation gaps and define canonical API examples and forbidden public implementation terms.
- T007-T013: Test `/docs`, `/openapi.json`, required request schema fields, `202` response, `400` response, accepted examples, and no Redis leakage.
- T014-T019: Configure FastAPI metadata, schema descriptions, route summaries, response examples, and 400 error behavior.

### US-002.2: Understand Command Processing Code

**Priority**: P2  
**Status**: Done  
**Outcome**: Public modules, classes, and functions have concise technical
documentation for command processing and extension.

Tasks:

- T020-T023: Test required module docstrings, public docstrings, registry/pipeline extension docs, and domain boundary documentation.
- T024-T040: Add concise documentation across domain, application, infrastructure, API, worker, and `TEST_COMMAND` modules.

### US-002.3: Use Documentation During Local Validation

**Priority**: P3  
**Status**: Done  
**Outcome**: README and generated docs help developers run, validate, and extend
the service locally.

Tasks:

- T041-T044: Test README docs URL, curl example, command-extension guidance, and external-client abstraction notes.
- T045-T049: Document Swagger URL, curl examples, validation instructions, extension flow, and queue abstraction notes in README.
- T050-T054: Run focused documentation/architecture/full tests, validate Docker docs, and review docstring concision.

---

## EPIC-003: Command Status Query

**Source**: `specs/003-command-status-query`  
**Status**: Done  
**Goal**: Add a read-only command status query contract with explicit success,
invalid-id, not-found, and documentation behavior.

### US-003.1: Check Submitted Command Status

**Priority**: P1  
**Status**: Done  
**Outcome**: External systems can query the status of a known command without
triggering queue or handler side effects.

Tasks:

- T001-T007: Inspect existing submission/repository/docs behavior and prepare the status use-case shell and examples.
- T008-T014: Test queued, processing, completed, and failed status views, API success, payload omission, and read-only behavior.
- T015-T019: Implement status request/result mapping, response schema, app wiring, route success path, and status lookup logs.

### US-003.2: Handle Unknown or Invalid Command Identifiers

**Priority**: P2  
**Status**: Done  
**Outcome**: Malformed command ids return HTTP 400 and unknown valid ids return
HTTP 404 without leaking storage internals.

Tasks:

- T020-T024: Test malformed id, unknown id, 400/404 API behavior, and internal-detail redaction.
- T025-T029: Add controlled errors, UUID validation, HTTP mapping, error schemas, and failure logs.

### US-003.3: Discover Status Query Contract

**Priority**: P3  
**Status**: Done  
**Outcome**: OpenAPI and README describe the status query contract and read-only
semantics.

Tasks:

- T030-T034: Test OpenAPI route metadata, success schema, 400/404 examples, and README status examples.
- T035-T038: Add OpenAPI path docs, schema examples, README status examples, and read-only notes.
- T039-T044: Run architecture, documentation, status query, API, full test, and Docker quickstart validation.

---

## EPIC-004: Command Persistence

**Source**: `specs/004-command-persistence`  
**Status**: Done  
**Goal**: Persist complete command execution records, including original
payload, response, errors, and lifecycle timestamps.

### US-004.1: Persist Submitted Command Before Queueing

**Priority**: P1  
**Status**: Done  
**Outcome**: Accepted commands are persisted with queued state and original
payload before queue publication.

Tasks:

- T001-T010: Inspect lifecycle, use cases, repositories, API docs, baseline tests, and persistence contract expectations.
- T011-T016: Test save-before-queue, payload retention, receipt timestamp, invalid command behavior, API retrievability, and Redis serialization.
- T017-T023: Extend `Command`, default queued record fields, submit logging, Redis serialization/deserialization, and memory repository support.

### US-004.2: Persist Processing Outcome and Execution History

**Priority**: P2  
**Status**: Done  
**Outcome**: Processing updates persist processing start, final status,
response or error, finish timestamp, and original payload.

Tasks:

- T024-T030: Test processing-before-pipeline, completed response, failed error, no-pipeline failure, payload retention, worker persistence, and context result persistence.
- T031-T039: Update command lifecycle methods, `ProcessCommand`, logging, `TEST_COMMAND` response, and Redis full-record updates.

### US-004.3: Retrieve Complete Command Execution Record

**Priority**: P3  
**Status**: Done  
**Outcome**: Clients can retrieve the complete persisted command record for
queued, completed, and failed states.

Tasks:

- T040-T045: Test complete record API responses, 404 behavior, use-case field coverage, and OpenAPI persistence schema.
- T046-T051: Extend retrieval result, response schema, route contract, examples, timestamp names, and README record examples.
- T052-T058: Run full/focused tests, domain isolation checks, Docker/RedisInsight validation, observability review, and quickstart updates.

---

## EPIC-005: Command Query

**Source**: `specs/005-command-query`  
**Status**: Done  
**Goal**: Split command query capabilities into complete detail, status-only,
and paginated status-filtered list endpoints.

### US-005.1: Retrieve Complete Command Details

**Priority**: P1  
**Status**: Done  
**Outcome**: External systems can query full command details by id with payload,
response, error, and lifecycle timestamps.

Tasks:

- T001-T010: Inspect existing retrieval, schemas, repository capabilities, baseline tests, fixtures, docs constants, architecture checks, and repository list support.
- T011-T016: Test full detail use case, malformed/unknown ids, API contract, read-only behavior, and OpenAPI docs.
- T017-T022: Create `GetCommand`, map persisted fields, add response schema, wire app state, update route, and add lookup logs.

### US-005.2: Retrieve Current Command Status Only

**Priority**: P2  
**Status**: Done  
**Outcome**: External systems can query a small status-only view without full
payload or execution details.

Tasks:

- T023-T028: Test exact status-only result, malformed/unknown ids, all statuses, field omission, read-only behavior, and OpenAPI docs.
- T029-T033: Refactor status result/schema, add `/status` route, add logs, and wire separate detail/status use cases.

### US-005.3: List Commands by Status

**Priority**: P3  
**Status**: Done  
**Outcome**: External systems can list command summaries filtered by status with
pagination.

Tasks:

- T034-T042: Test status filters, default/explicit pagination, invalid inputs, memory/Redis repository listing, API summaries, read-only behavior, and OpenAPI docs.
- T043-T050: Create `ListCommands`, validate status/pagination, add schemas, wire app state, add route, map errors, and log list queries safely.
- T051-T058: Update README/docs tests, run full and focused tests, verify domain isolation, Docker quickstart, OpenAPI output, and ADR/documentation notes.

---

## EPIC-006: Command Callback Persistence

**Source**: `specs/006-command-callback-persistence`  
**Status**: Done  
**Goal**: Add optional `external_id` and callback support, move durable command
persistence to PostgreSQL, audit callback delivery, and support latest lookup by
external id.

### US-006.1: Submit Traceable Async Command

**Priority**: P1  
**Status**: Done  
**Outcome**: Command submission accepts optional `external_id` and optional
`callback`, persists the traceable command before queueing, and returns queued
status immediately.

Tasks:

- T001-T018: Inspect current implementation, run baseline tests, add PostgreSQL/HTTP dependencies, document env vars, add callback status enum, extend ports/entity/repositories, add PostgreSQL service, and add documentation checks.
- T019-T026: Test minimal/full submission, callback required/not-required behavior, validations, no API handler execution, and PostgreSQL queued insert/read behavior.
- T027-T036: Update API schemas/routes, `SubmitCommand`, PostgreSQL repository insert/get, runtime wiring, OpenAPI examples, Docker dependencies, and focused US1 tests.

### US-006.2: Process Command and Persist Outcome

**Priority**: P2  
**Status**: Done  
**Outcome**: Worker processing loads commands from durable storage, records
processing transitions, stores `response_payload` on success, and stores
`error_message` on failure.

Tasks:

- T037-T042: Test success, handler failure, missing pipeline, worker delegation, context result sharing, and PostgreSQL processing updates.
- T043-T052: Update lifecycle methods, `ProcessCommand`, registry errors, pipeline result conventions, `TEST_COMMAND`, PostgreSQL updates, worker wiring, and focused US2 tests.

### US-006.3: Deliver Optional Callback

**Priority**: P3  
**Status**: Done  
**Outcome**: Callback delivery runs after final processing status only when a
non-blank callback was provided; success/failure delivery is audited separately
from command processing status.

Tasks:

- T053-T059: Test callback payload contracts, success callback, failure callback, no callback, callback failure auditing, HTTP adapter behavior, and PostgreSQL callback fields.
- T060-T070: Add callback orchestration, payload builder, no-op callback behavior, HTTP callback client, callback lifecycle methods, repository updates, worker injection, callback logs, and focused US3 tests.

### US-006.4: Query Commands by Command or External Identifier

**Priority**: P4  
**Status**: Done  
**Outcome**: External systems can query full command records, status-only
records including callback status, and the latest command for an external id.

Tasks:

- T071-T075: Test full detail callback fields, status-only callback status, latest external-id lookup, 400/404 behavior, and repository ordering.
- T076-T087: Update response schemas, use-case mappings, create `GetCommandByExternalId`, order routes safely, update repositories/indexes, OpenAPI docs, and focused US4 tests.
- T088-T096: Update README, add ADR-0009, revise Redis ADR, update quickstart, run full tests, validate Docker Compose, verify curl quickstart, verify Swagger, and run final architecture/docs checks.

---

## Cross-Cutting Backlog Themes

These themes appear across multiple epics and define ongoing project standards.

### Architecture

- Keep domain free from FastAPI, Redis, PostgreSQL, Docker, HTTP clients, and infrastructure imports.
- Access queueing, persistence, and callback delivery only through ports.
- Keep worker flow type-agnostic; command-specific behavior belongs in pipelines and handlers.

### Contracts

- Maintain explicit Pydantic/OpenAPI contracts for command submission, detail,
  status, list, external-id lookup, validation errors, and not-found errors.
- Keep public contracts free of queue, broker, repository, and storage
  implementation details.

### Observability

- Log command submission, persistence, queue publication, processing start,
  success, failure, callback attempt, callback success, and callback failure.
- Persist traceable state transitions and error messages on every command.

### Testing

- Add tests before or alongside implementation for new behavior.
- Cover success paths, validation paths, handler failures, infrastructure
  adapters or fakes, documentation contracts, and architecture boundaries.
- Validate with full pytest and focused tests named in the source tasks.

### Documentation

- Keep README focused on quickstart, local execution, API usage, worker
  behavior, observability, and extension points.
- Store architectural decisions in `docs/adr/`.
- Keep this backlog aligned whenever a new `specs/###-*` feature is added.
