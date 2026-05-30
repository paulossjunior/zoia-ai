# Feature Specification: Command Status Query

**Feature Branch**: `003-command-status-query`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "crie uma rota para saber se o comando foi processado. por exemplo adicionar GET /commands/{command_id}"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check Submitted Command Status (Priority: P1)

As an external integrator, I want to query a command by the identifier returned when I submitted it so that I can know whether the command is still waiting, currently processing, completed, or failed.

**Why this priority**: The asynchronous command API already returns immediately, so clients need a follow-up status view to observe the outcome without accessing internal systems.

**Independent Test**: Can be tested by submitting a valid command, using the returned command identifier to query its status, and confirming the response exposes the command lifecycle state and timestamps.

**Acceptance Scenarios**:

1. **Given** a command was accepted and a command identifier was returned, **When** the client queries that identifier, **Then** the system returns the command identifier and its current status.
2. **Given** a command is processed successfully by a worker, **When** the client queries that identifier after processing, **Then** the system returns status `completed` and a completion timestamp.
3. **Given** a command fails during processing, **When** the client queries that identifier after processing, **Then** the system returns status `failed`, a completion timestamp, and an error message.

---

### User Story 2 - Handle Unknown or Invalid Command Identifiers (Priority: P2)

As an external integrator, I want clear responses when a command identifier is invalid or unknown so that I can distinguish client mistakes from commands that are still being processed.

**Why this priority**: Status lookup is an integration surface; ambiguous errors would make external monitoring unreliable.

**Independent Test**: Can be tested by querying a malformed identifier and a well-formed identifier that does not exist, then confirming each response has the expected error status and body.

**Acceptance Scenarios**:

1. **Given** a malformed command identifier, **When** the client queries command status, **Then** the system rejects the request as invalid.
2. **Given** a well-formed command identifier that is not known to the system, **When** the client queries command status, **Then** the system returns a not-found response.
3. **Given** any failed status lookup, **When** the client receives the error, **Then** the response body includes a concise reason without exposing internal storage or queue details.

---

### User Story 3 - Discover Status Query Contract (Priority: P3)

As a developer or tester, I want the status query contract documented alongside command submission so that I can validate asynchronous processing end-to-end using documented examples.

**Why this priority**: The status query completes the observable command workflow and should be discoverable through the same documentation surface as command submission.

**Independent Test**: Can be tested by reviewing the public command documentation and confirming the status query includes success, invalid identifier, and not-found examples.

**Acceptance Scenarios**:

1. **Given** the documentation is available, **When** a developer reviews command endpoints, **Then** the status query is listed with its required command identifier.
2. **Given** the developer reads the status query examples, **When** they compare them with actual responses, **Then** the documented success and error bodies match runtime behavior.

### Edge Cases

- The command is accepted but has not been consumed yet: the status query returns `queued`.
- The worker has started but not finished: the status query returns `processing`.
- The worker completes successfully: the status query returns `completed`.
- The worker records a failure: the status query returns `failed` with `error_message`.
- The command identifier is malformed: the request is rejected as invalid.
- The command identifier is well formed but not found: the request returns not found.
- The status query must not create, enqueue, or process commands.
- External documentation must not require clients to know queue or storage implementation details.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose `GET /commands/{command_id}` so clients can query command status using the command identifier returned by command submission.
- **FR-002**: A successful status query MUST return `command_id`, `type`, `status`, `created_at`, `started_at`, `completed_at`, and `error_message`.
- **FR-003**: The status field MUST use only the explicit command lifecycle states: `queued`, `processing`, `completed`, or `failed`.
- **FR-004**: Queued commands MUST return `started_at`, `completed_at`, and `error_message` as empty values.
- **FR-005**: Processing commands MUST return `started_at` and MUST keep `completed_at` empty until processing finishes.
- **FR-006**: Completed commands MUST return `completed_at` and MUST keep `error_message` empty.
- **FR-007**: Failed commands MUST return `completed_at` and a clear `error_message`.
- **FR-008**: The status query MUST NOT return the original command payload by default.
- **FR-009**: The status query MUST NOT enqueue commands, execute handlers, or otherwise trigger command processing.
- **FR-010**: The system MUST reject malformed command identifiers with a validation error response.
- **FR-011**: The system MUST return a not-found response for well-formed command identifiers that are not known to the system.
- **FR-012**: The status query contract MUST document success, invalid identifier, and not-found responses.
- **FR-013**: Public documentation MUST describe status lookup as an external observation contract without exposing internal queue or storage implementation details.

### Key Entities

- **Command Status View**: External representation of a command's current lifecycle state, timestamps, and failure reason.
- **Command Identifier**: Unique value returned during command submission and later used to query command status.
- **Status Lookup Error**: Public error response for malformed or unknown command identifiers.

### Contracts

- **Command Status Query Contract**: `GET /commands/{command_id}` queries by command identifier and returns the command status view on success.
- **Successful Status Response**:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "status": "completed",
  "created_at": "2026-05-30T19:00:00Z",
  "started_at": "2026-05-30T19:00:01Z",
  "completed_at": "2026-05-30T19:00:02Z",
  "error_message": null
}
```

- **Invalid Identifier Error Contract**:

```json
{
  "detail": "invalid command_id"
}
```

- **Not Found Error Contract**:

```json
{
  "detail": "command not found"
}
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of accepted commands can be queried by their returned command identifier while their record exists.
- **SC-002**: A client can determine whether a command is `queued`, `processing`, `completed`, or `failed` from a single status query response.
- **SC-003**: 100% of malformed command identifier queries return a validation error instead of an ambiguous status.
- **SC-004**: 100% of unknown but well-formed command identifier queries return a not-found response.
- **SC-005**: Documentation examples for status lookup match actual success and error responses.

## Assumptions

- The command identifier format remains the same identifier format generated during command submission.
- The status query is read-only and does not change command state.
- The original command payload is not returned in v1 to avoid exposing submitted data unnecessarily.
- Status records are available for as long as the command store retains them.
- Authentication and authorization are outside the current scope because the existing command submission API is already unauthenticated in this local service.
