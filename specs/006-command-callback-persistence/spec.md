# Feature Specification: Command Callback Persistence

**Feature Branch**: `006-command-callback-persistence`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Criar uma funcionalidade de processamento assíncrono de comandos com persistência, rastreabilidade, consulta e callback opcional."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit Traceable Async Command (Priority: P1)

As an external system, I want to submit a command with a type, payload, optional business identifier, and optional callback URL so that the command is accepted for asynchronous processing and can be tracked later.

**Why this priority**: Submission is the entry point for every other workflow. The command must be validated, identified, persisted, and queued before any processing or callback can occur.

**Independent Test**: Can be tested by submitting a valid command with and without optional fields, then confirming the response returns a command id and queued status while the persisted record contains the original request data.

**Acceptance Scenarios**:

1. **Given** a valid command with type and payload, **When** it is submitted, **Then** the system returns a generated command id and status `queued`.
2. **Given** a command includes `external_id`, **When** it is accepted, **Then** the command record stores that external business identifier.
3. **Given** a command includes a callback URL, **When** it is accepted, **Then** the command record stores the callback URL and marks callback delivery as pending.
4. **Given** a command omits callback, **When** it is accepted, **Then** callback delivery is marked as not required.
5. **Given** a command is missing type or payload, **When** it is submitted, **Then** the system rejects the request with a validation error and creates no command.

---

### User Story 2 - Process Command and Persist Outcome (Priority: P2)

As an operator, I want command processing to update status, timestamps, responses, and errors so that every command is auditable from receipt through completion or failure.

**Why this priority**: Processing outcome persistence is required to make asynchronous execution reliable and explainable after the initial request has returned.

**Independent Test**: Can be tested by processing commands through success and failure paths, then retrieving the persisted records and verifying status, response payload, error message, and timestamps.

**Acceptance Scenarios**:

1. **Given** a queued command, **When** a worker starts processing it, **Then** the command status becomes `processing` and processing start time is recorded.
2. **Given** command processing succeeds, **When** processing finishes, **Then** status becomes `completed`, response payload is persisted, and processing finish time is recorded.
3. **Given** command processing fails, **When** processing finishes, **Then** status becomes `failed`, error message is persisted, and processing finish time is recorded.
4. **Given** a command type has a registered processing pipeline, **When** it is processed, **Then** the pipeline is resolved by type and executed through a handler chain.
5. **Given** no pipeline exists for a command type, **When** processing is attempted, **Then** the command is marked failed with a clear error message.

---

### User Story 3 - Deliver Optional Callback (Priority: P3)

As an external system, I want to receive the command result by callback when I provide a callback URL so that my system can react to completion without polling.

**Why this priority**: Callback delivery improves integration experience, but it must happen only after command processing has produced a final success or failure outcome.

**Independent Test**: Can be tested by processing commands with and without callback URLs and verifying that callbacks are attempted only when requested, while command outcomes remain persisted regardless of callback success or failure.

**Acceptance Scenarios**:

1. **Given** a command has a callback URL, **When** processing finishes successfully, **Then** the system sends the success result to the callback URL.
2. **Given** a command has a callback URL, **When** processing fails, **Then** the system sends the failure result to the callback URL.
3. **Given** a command has no callback URL, **When** processing finishes, **Then** the system performs no external callback request.
4. **Given** callback delivery succeeds, **When** the attempt is recorded, **Then** callback status becomes `sent` and callback sent time is stored.
5. **Given** callback delivery fails, **When** the attempt is recorded, **Then** callback status becomes `failed`, callback error message is stored, and the command processing result remains unchanged.

---

### User Story 4 - Query Commands by Command or External Identifier (Priority: P4)

As an external system, I want to query commands by command id, status, or external business id so that I can track command execution even when no callback is configured or callback delivery fails.

**Why this priority**: Querying completes the traceability loop and provides an operational fallback for integrations.

**Independent Test**: Can be tested by creating commands with command ids and repeated external ids, then confirming lookup by command id, status-only lookup, and most-recent lookup by external id.

**Acceptance Scenarios**:

1. **Given** a command exists, **When** it is queried by command id, **Then** the system returns the complete command record.
2. **Given** a command exists, **When** status is queried by command id, **Then** the system returns only command id, status, and callback status.
3. **Given** multiple commands share an external id, **When** that external id is queried, **Then** the system returns the most recent matching command.
4. **Given** no command exists for a command id or external id, **When** the query is executed, **Then** the system returns a not-found error.

### Edge Cases

- Callback URL is omitted, null, or blank.
- Callback URL is present but delivery fails because the destination is unavailable or returns an unsuccessful result.
- Callback delivery fails after command processing has completed successfully.
- Command processing fails before callback delivery is attempted.
- A command type cannot be resolved to a pipeline.
- A handler in the processing chain interrupts execution with an error.
- Multiple commands use the same external id.
- A command is queried while still queued or processing.
- A command id or external id does not exist.
- Required fields are missing or have invalid shapes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose command submission for asynchronous processing.
- **FR-002**: Command submission MUST require `type` and `payload`.
- **FR-003**: Command submission MUST accept optional `external_id`.
- **FR-004**: Command submission MUST accept optional `callback`.
- **FR-005**: The system MUST generate a unique `command_id` for every accepted command.
- **FR-006**: The system MUST persist every valid command before queueing it for processing.
- **FR-007**: The system MUST store command id, type, original payload, optional external id, optional callback URL, current status, response payload, error message, callback status, callback error message, retry count, and lifecycle timestamps.
- **FR-008**: The system MUST mark accepted commands as `queued`.
- **FR-009**: The system MUST mark callback status as `pending` when a callback URL is provided.
- **FR-010**: The system MUST mark callback status as `not_required` when no callback URL is provided.
- **FR-011**: The system MUST enqueue valid commands for asynchronous processing after persistence.
- **FR-012**: The command API MUST return immediately without waiting for processing to finish.
- **FR-013**: Workers MUST load the persisted command before processing.
- **FR-014**: Workers MUST mark a command as `processing` when processing starts.
- **FR-015**: Workers MUST resolve the processing pipeline by command type.
- **FR-016**: Each command type MUST be processed by its own pipeline using Chain of Responsibility.
- **FR-017**: The system MUST persist response payload when processing succeeds.
- **FR-018**: The system MUST persist error message when processing fails.
- **FR-019**: The system MUST mark command status as `completed` after successful processing.
- **FR-020**: The system MUST mark command status as `failed` after failed processing.
- **FR-021**: The system MUST send callback delivery only when the original command included a non-blank callback URL.
- **FR-022**: Callback delivery MUST be attempted for both successful and failed processing outcomes when callback is configured.
- **FR-023**: Callback delivery failure MUST NOT change a successful command processing status to failed.
- **FR-024**: The system MUST preserve processing result data even when callback delivery fails.
- **FR-025**: The system MUST record callback status, callback error message, and callback sent time when applicable.
- **FR-026**: The system MUST allow querying a command by command id.
- **FR-027**: The system MUST allow querying command status and callback status by command id.
- **FR-028**: The system MUST allow querying the most recent command by external id.
- **FR-029**: The system MUST return not-found errors for unknown command ids and unknown external ids.
- **FR-030**: The system MUST keep command records available after processing completes or fails.
- **FR-031**: Worker errors and callback errors MUST be recorded with clear messages.

### Key Entities

- **Command**: Persisted asynchronous work item containing command id, type, payload, optional external id, optional callback URL, processing status, processing outcome, callback audit fields, retry count, and timestamps.
- **Command Status**: Processing lifecycle state: `queued`, `processing`, `completed`, or `failed`.
- **Callback Status**: Callback lifecycle state: `not_required`, `pending`, `sent`, or `failed`.
- **Command Pipeline**: Type-specific handler chain that validates payload, checks idempotency, executes business logic, and records audit information.
- **Callback Delivery**: Attempt to send the final processing result to the configured callback URL.

### Contracts

- **Submit Command Contract**: Accepts `type`, `payload`, optional `external_id`, and optional `callback`; returns `command_id` and `queued` status.
- **Command Detail Contract**: Query by command id and return the complete persisted command record, including callback audit fields.
- **Command Status Contract**: Query by command id and return command id, command status, and callback status.
- **External Id Lookup Contract**: Query by external id and return the most recent command associated with that external id.
- **Callback Contract**: When callback is configured, send final success or failure status and payload to the configured URL.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid accepted commands have a persisted record before queueing.
- **SC-002**: 100% of invalid submissions missing type or payload are rejected without creating a command.
- **SC-003**: 100% of successfully processed commands persist final status, response payload, and finish timestamp.
- **SC-004**: 100% of failed commands persist final status, error message, and finish timestamp.
- **SC-005**: 100% of commands without callback complete without any external callback attempt.
- **SC-006**: 100% of commands with callback record callback status after processing completion.
- **SC-007**: 100% of callback failures preserve the command processing outcome and remain available for query.
- **SC-008**: 100% of known command ids can be queried while their records are retained.
- **SC-009**: External id lookup returns the most recent matching command when multiple records share the same external id.

## Assumptions

- Callback delivery is attempted after command processing reaches a final status.
- Callback payload contains the external id only when it was provided in the original command.
- Blank callback values are treated as not provided.
- External ids are not unique and may be reused by the source system.
- The most recent command for an external id is determined by request receipt time.
- Retry policy details for callback delivery beyond recording retry count are outside this specification unless clarified in a later feature.
- Specific storage and queue products are implementation constraints to be handled during planning; public behavior remains defined by the contracts above.
