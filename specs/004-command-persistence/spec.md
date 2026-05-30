# Feature Specification: Command Persistence

**Feature Branch**: `004-command-persistence`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Persistência de Comandos. Garantir rastreabilidade completa de todos os comandos recebidos e processados pelo sistema, persistindo payload original, status, resposta, erro e timestamps, com consulta posterior por identificador."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persist Submitted Command Before Queueing (Priority: P1)

As an external integrator, I want every accepted command to be recorded before it is queued so that the command can be traced even if asynchronous processing has not started yet.

**Why this priority**: Persistence before queueing is the foundation for traceability and prevents accepted commands from disappearing between HTTP acknowledgement and worker execution.

**Independent Test**: Can be tested by submitting a valid command, verifying that the command record exists before queue publication, and confirming the record contains id, type, original payload, queued status, and receipt timestamp.

**Acceptance Scenarios**:

1. **Given** a valid command request, **When** the system accepts it, **Then** the command is persisted with status `queued` before it is queued for processing.
2. **Given** a command is persisted after submission, **When** the record is retrieved by identifier, **Then** it contains the generated id, command type, original payload, current status, and request receipt timestamp.
3. **Given** command submission fails validation, **When** the request is rejected, **Then** no command record is created and nothing is queued.

---

### User Story 2 - Persist Processing Outcome and Execution History (Priority: P2)

As an operator or developer, I want processing start, finish, response, and error details persisted so that I can audit what happened during asynchronous execution.

**Why this priority**: The worker owns the final outcome, and operators need durable evidence of successful and failed processing after the HTTP request has already returned.

**Independent Test**: Can be tested by processing commands through success and failure paths, then retrieving each command and confirming status transitions, timestamps, response, or error message were persisted.

**Acceptance Scenarios**:

1. **Given** a queued command, **When** a worker starts processing it, **Then** the command status becomes `processing` and processing start time is recorded.
2. **Given** a command handler succeeds, **When** processing finishes, **Then** the command status becomes `completed`, processing finish time is recorded, and the produced response is persisted.
3. **Given** a command handler fails, **When** processing finishes, **Then** the command status becomes `failed`, processing finish time is recorded, and the error message is persisted.

---

### User Story 3 - Retrieve Complete Command Execution Record (Priority: P3)

As an external integrator or support user, I want to retrieve the complete execution record for a command so that I can inspect the current state and full persisted history of that command.

**Why this priority**: Status lookup shows the current state, but support and audit workflows require the payload, response, error, and lifecycle timestamps together.

**Independent Test**: Can be tested by retrieving a processed command by identifier and confirming the response contains all persisted fields and reflects the latest state.

**Acceptance Scenarios**:

1. **Given** a command exists, **When** it is retrieved by identifier, **Then** the system returns its id, type, payload, status, response, error message, and lifecycle timestamps.
2. **Given** a command has completed successfully, **When** it is retrieved by identifier, **Then** the persisted response is available and the error message is empty.
3. **Given** a command has failed, **When** it is retrieved by identifier, **Then** the persisted error message is available and the response is empty.

### Edge Cases

- Queue publication fails after command persistence: the command record remains available with queued status for investigation or recovery.
- Worker starts processing but handler fails: status changes to `failed`, processing finish time is recorded, and the error message is persisted.
- Worker resolves no handler or pipeline for the command type: the command is marked failed with a clear error message.
- Handler produces no response on success: the command is still marked completed and response remains empty.
- A command is queried before processing starts: the record shows queued status and no processing timestamps.
- A command is queried while processing is active: the record shows processing status and processing start time.
- A command identifier is unknown: retrieval returns a not-found response.
- Persisted payload, response, and error fields must remain associated with the same command identifier throughout the lifecycle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST persist every valid received command before sending it to the processing queue.
- **FR-002**: The system MUST store a unique command identifier for every persisted command.
- **FR-003**: The system MUST store the command type for every persisted command.
- **FR-004**: The system MUST store the original payload received for every persisted command.
- **FR-005**: The system MUST store the current command status as one of `queued`, `processing`, `completed`, or `failed`.
- **FR-006**: The system MUST store the processing response when command processing succeeds and a response is produced.
- **FR-007**: The system MUST store a clear error message when command processing fails.
- **FR-008**: The system MUST store the date and time when the command request was received.
- **FR-009**: The system MUST store the date and time when processing starts.
- **FR-010**: The system MUST store the date and time when processing finishes.
- **FR-011**: The system MUST update persisted status to `processing` before executing command-specific business logic.
- **FR-012**: The system MUST update persisted status to `completed` after successful processing.
- **FR-013**: The system MUST update persisted status to `failed` after processing failure.
- **FR-014**: The system MUST allow retrieving the current state of a command by its identifier.
- **FR-015**: The system MUST allow retrieving the complete execution record for a command by its identifier.
- **FR-016**: The complete execution record MUST include id, type, payload, status, response, error message, request received time, processing start time, and processing finish time.
- **FR-017**: The system MUST preserve command records after processing completes or fails.
- **FR-018**: The system MUST NOT lose the original payload when status or processing outcome is updated.
- **FR-019**: The system MUST document the persisted command record contract, including empty values for fields not yet available.

### Key Entities

- **Command**: Persisted record representing a command received for asynchronous processing. Key attributes: id, type, payload, status, response, error message, request received time, processing start time, and processing finish time.
- **Command Execution Record**: Full retrievable view of a command lifecycle, including submitted data, current status, processing outcome, and timestamps.
- **Command Processing Response**: Structured result produced by successful command processing, when available.
- **Command Processing Error**: Clear failure message persisted when processing cannot complete successfully.

### Contracts

- **Persisted Command Record Contract**: Defines the fields stored and returned for command traceability: `id`, `type`, `payload`, `status`, `response`, `error_message`, `request_received_at`, `processing_started_at`, and `processing_finished_at`.
- **Command Retrieval Contract**: Query by command identifier and return the full execution record when found, or a not-found error when no command exists.
- **Status Values Contract**: Allowed command statuses are `queued`, `processing`, `completed`, and `failed`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid accepted commands have a persisted record before queue publication.
- **SC-002**: 100% of persisted commands can be retrieved by identifier while the record exists.
- **SC-003**: 100% of successfully processed commands retain their original payload and persist their processing response when one is produced.
- **SC-004**: 100% of failed commands retain their original payload and persist a non-empty error message.
- **SC-005**: 100% of processed commands include request receipt time and processing finish time, with processing start time recorded before completion or failure.
- **SC-006**: A support user can determine a command's current status and full execution record from a single retrieval operation.

## Assumptions

- Existing command identifiers remain globally unique for command retrieval.
- The complete execution record is intended for operational/support use and may include the original payload.
- Response is optional because some command handlers may complete successfully without producing a structured response.
- Error message is optional until a command fails.
- The specific storage technology and retention policy are implementation details to be decided during planning.
