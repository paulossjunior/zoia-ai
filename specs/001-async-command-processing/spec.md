# Feature Specification: Async Command Processing

**Feature Branch**: `001-async-command-processing`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Criar uma capacidade de processamento assíncrono de comandos para permitir que sistemas externos enviem comandos com type e payload, recebam confirmação imediata, e tenham workers independentes consumindo comandos por tipo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit Valid Command (Priority: P1)

As an external system, I want to submit a command for later processing so that my request is acknowledged quickly without waiting for the command's business work to finish.

**Why this priority**: This is the core value of the feature: external systems can hand off work asynchronously and continue their own flow.

**Independent Test**: Can be fully tested by submitting a valid command with `type` and `payload` and verifying that an acknowledgement with a unique command identifier and `queued` status is returned before any command-specific processing is completed.

**Acceptance Scenarios**:

1. **Given** an external system sends a valid command to `POST /commands`, **When** the command contains a non-empty `type` and a `payload` object, **Then** the system returns an acknowledgement containing `command_id` and `status: queued`.
2. **Given** a valid command is received, **When** the acknowledgement is returned, **Then** the command has already been recorded and is available for asynchronous processing.
3. **Given** command-specific processing may take time, **When** the external system submits the command, **Then** the client response is not delayed until that processing completes.

---

### User Story 2 - Reject Invalid Command (Priority: P1)

As an external system, I want invalid command submissions to be rejected clearly so that I can correct request data without creating unusable queued work.

**Why this priority**: Invalid data must not enter the asynchronous workflow, otherwise workers would spend effort on commands that should have been rejected at the boundary.

**Independent Test**: Can be fully tested by submitting commands missing `type`, missing `payload`, or using an invalid payload shape and verifying that the system returns HTTP 400 and does not queue the command.

**Acceptance Scenarios**:

1. **Given** a command submission is missing `type`, **When** the request is validated, **Then** the system returns HTTP 400 and no command is queued.
2. **Given** a command submission is missing `payload`, **When** the request is validated, **Then** the system returns HTTP 400 and no command is queued.
3. **Given** a command submission has a `payload` that is not an object, **When** the request is validated, **Then** the system returns HTTP 400 and no command is queued.

---

### User Story 3 - Process Queued Command (Priority: P2)

As a worker operator, I want queued commands to be consumed and routed to the correct handler so that each command type executes its intended business behavior independently from request handling.

**Why this priority**: Once commands can be accepted, the system must reliably execute them through workers to deliver the intended business outcome.

**Independent Test**: Can be fully tested by registering a handler for a command type, submitting a command of that type, running a worker, and verifying that the matching handler is executed and the command status changes to `completed`.

**Acceptance Scenarios**:

1. **Given** a queued command with a known `type`, **When** a worker consumes it, **Then** the worker selects the handler registered for that `type`.
2. **Given** a selected handler completes successfully, **When** the worker finishes execution, **Then** the command status becomes `completed` and `completed_at` is recorded.
3. **Given** a command begins worker execution, **When** processing starts, **Then** the command status becomes `processing` and `started_at` is recorded.

---

### User Story 4 - Record Processing Failure (Priority: P2)

As an operations user, I want processing failures to be recorded on the command so that failed commands can be diagnosed and handled after the client has already received acknowledgement.

**Why this priority**: Asynchronous systems need visible failure outcomes because the submitting client is not waiting for execution results.

**Independent Test**: Can be fully tested by registering a handler that fails, processing a queued command with that handler, and verifying that the command status changes to `failed` with a useful error message.

**Acceptance Scenarios**:

1. **Given** a handler fails while executing a command, **When** the worker records the outcome, **Then** the command status becomes `failed`.
2. **Given** command processing fails, **When** the failure is recorded, **Then** `error_message` contains enough information for operators to identify the failure category without exposing sensitive payload data.
3. **Given** a command type has no registered handler, **When** a worker attempts to process it, **Then** the command is marked `failed` with an error indicating that no handler was available.

---

### User Story 5 - Add New Command Handler (Priority: P3)

As a development team, I want new command types to be added by registering new handlers so that the main submission and processing flow does not need to change for each new business command.

**Why this priority**: Extensibility keeps the asynchronous command capability useful as new command types are introduced.

**Independent Test**: Can be fully tested by adding a handler for a new `type`, submitting a command with that type, and verifying that the worker resolves and executes the new handler without changing the command submission flow.

**Acceptance Scenarios**:

1. **Given** a new command handler has been registered for a new `type`, **When** a worker consumes a command of that type, **Then** the new handler is selected.
2. **Given** the command submission flow is already available, **When** a new handler is added, **Then** external systems continue using the same command submission contract.

### Edge Cases

- A command submission contains an empty or whitespace-only `type`: the request is rejected with HTTP 400 and nothing is queued.
- A command submission contains malformed request content: the request is rejected with HTTP 400 and nothing is queued.
- The command is recorded but cannot be queued: the system does not return `queued`; it reports the submission failure and preserves enough record state for diagnosis.
- A queued command is consumed by a worker but has no matching handler: the command is marked `failed`.
- A handler raises an unexpected error: the command is marked `failed`, `completed_at` is recorded as the time processing ended, and a safe error summary is stored.
- Multiple commands are submitted close together: each receives a distinct command identifier and can be tracked independently.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a command submission interface at `POST /commands`.
- **FR-002**: The command submission request MUST require a non-empty `type` field.
- **FR-003**: The command submission request MUST require a `payload` field containing an object.
- **FR-004**: The system MUST reject invalid command submissions with HTTP 400 before recording or queueing the command.
- **FR-005**: The system MUST generate a unique identifier for each accepted command.
- **FR-006**: The system MUST record each accepted command with `id`, `type`, `payload`, `status`, and `created_at` before making it available for asynchronous processing.
- **FR-007**: The system MUST set the initial status of each accepted command to `queued`.
- **FR-008**: The system MUST return an acknowledgement containing `command_id` and `status: queued` immediately after successful validation, recording, and queue registration.
- **FR-009**: The system MUST ensure command-specific business processing does not occur during the client submission request.
- **FR-010**: Workers MUST consume queued commands independently from the command submission request flow.
- **FR-011**: Workers MUST update a command to `processing` and record `started_at` when execution begins.
- **FR-012**: Workers MUST select command execution behavior based on the command `type`.
- **FR-013**: Workers MUST execute the handler associated with the command `type`.
- **FR-014**: Workers MUST update successfully processed commands to `completed` and record `completed_at`.
- **FR-015**: Workers MUST update failed commands to `failed`, record `completed_at`, and store a safe `error_message`.
- **FR-016**: The system MUST support registering new handlers without changing the main command submission or worker processing flow.
- **FR-017**: Business logic MUST depend on an abstract command queue capability, not on a specific queue technology.
- **FR-018**: The command store MUST allow command status and timestamps to be updated throughout the command lifecycle.

### Key Entities

- **Command**: A unit of work submitted by an external system for asynchronous processing. Key attributes: `id`, `type`, `payload`, `status`, `created_at`, optional `started_at`, optional `completed_at`, and optional `error_message`.
- **CommandStatus**: The lifecycle state of a command. Allowed values: `queued`, `processing`, `completed`, `failed`.
- **Command Handler**: A registered behavior that knows how to execute commands for a specific command `type`.
- **ExternalSystem**: A client system that submits commands and receives immediate acknowledgement.
- **Worker**: An independent processor that consumes queued commands, resolves handlers, executes them, and records outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid command submissions receive an acknowledgement with a unique command identifier and `queued` status.
- **SC-002**: 100% of invalid submissions missing `type` or `payload` are rejected with HTTP 400 and are not queued.
- **SC-003**: At least 95% of accepted submissions receive acknowledgement within 500 milliseconds under normal operating load, excluding client network latency.
- **SC-004**: 100% of commands processed successfully by a handler reach `completed` status with a completion timestamp.
- **SC-005**: 100% of handler failures and unresolved command types reach `failed` status with a safe error summary.
- **SC-006**: A new command type can be added through handler registration without changing the command submission contract.

## Assumptions

- External systems are already authorized to submit commands through the application's existing access controls.
- The first version validates the generic command envelope (`type` and `payload`) and leaves command-type-specific payload validation to the relevant handler or a handler-owned validation step.
- The acknowledgement response reports submission acceptance, not final business execution success.
- Commands are tracked individually and are not assumed to execute in the same order they were submitted unless a future command type explicitly requires ordering.
- The queue mechanism is treated as an internal capability; any specific queue product is an implementation detail and must not leak into business logic.
