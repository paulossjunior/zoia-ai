# Feature Specification: Command Query

**Feature Branch**: `005-command-query`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Consulta de Comandos. Permitir acompanhar e consultar comandos enviados anteriormente, incluindo status, resultado e informações de erro. Use cases: GetCommand, GetCommandStatus, ListCommandsByStatus. Endpoints: GET /commands/{id}, GET /commands/{id}/status, GET /commands?status=..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Complete Command Details (Priority: P1)

As an external system, I want to retrieve the full persisted details of a command by its identifier so that I can inspect its submitted data, current state, processing result, and any error information.

**Why this priority**: Complete command lookup is the primary support and integration workflow. It gives the caller enough information to understand what happened to one previously submitted command.

**Independent Test**: Can be tested by querying an existing command identifier and confirming the response contains the command id, type, status, payload, response, error message, and lifecycle timestamps.

**Acceptance Scenarios**:

1. **Given** a command exists, **When** `GET /commands/{id}` is executed, **Then** the system returns the complete persisted command details.
2. **Given** a command completed successfully, **When** it is retrieved by id, **Then** the response includes the persisted processing result and no error message.
3. **Given** a command failed during processing, **When** it is retrieved by id, **Then** the response includes the persisted error message and no processing result.
4. **Given** no command exists for the supplied id, **When** `GET /commands/{id}` is executed, **Then** the system returns a not-found error.

---

### User Story 2 - Retrieve Current Command Status Only (Priority: P2)

As an external system, I want to retrieve only the current status of a command so that I can poll lightweight state changes without receiving the full payload or processing details.

**Why this priority**: Polling status is a common integration need and avoids returning the full command record when the caller only needs the lifecycle state.

**Independent Test**: Can be tested by querying an existing command identifier through the status-only lookup and confirming the response contains only the command id and current status.

**Acceptance Scenarios**:

1. **Given** a command exists, **When** `GET /commands/{id}/status` is executed, **Then** the system returns only the command id and current status.
2. **Given** a command is queued, processing, completed, or failed, **When** status is queried, **Then** the returned status matches the persisted command state.
3. **Given** no command exists for the supplied id, **When** `GET /commands/{id}/status` is executed, **Then** the system returns a not-found error.

---

### User Story 3 - List Commands by Status (Priority: P3)

As an external system, I want to list commands filtered by status so that I can monitor groups of queued, processing, completed, or failed commands.

**Why this priority**: Operators and integrations need a way to inspect command groups, especially failed commands, but this is less urgent than retrieving one known command.

**Independent Test**: Can be tested by creating commands with multiple statuses, querying the list with a status filter, and confirming only matching commands are returned with pagination metadata.

**Acceptance Scenarios**:

1. **Given** commands exist with different statuses, **When** `GET /commands?status=failed` is executed, **Then** the response includes only failed commands.
2. **Given** the result set is larger than one page, **When** a page and page size are supplied, **Then** the system returns the requested page and pagination metadata.
3. **Given** an invalid status filter is supplied, **When** the list endpoint is executed, **Then** the system rejects the request with a validation error.
4. **Given** no commands match the supplied status, **When** the list endpoint is executed, **Then** the system returns an empty list with total zero.

### Edge Cases

- A malformed command identifier is supplied for detail or status lookup.
- A valid command identifier is supplied but no matching command exists.
- A status filter is not one of `queued`, `processing`, `completed`, or `failed`.
- Page or page size parameters are less than one.
- The requested page is beyond the number of available matching commands.
- A command has no processing response because it has not completed or completed without producing a result.
- A command has no error message because it has not failed.
- A command is queried while processing is active and has no finish timestamp yet.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow retrieving a command by its identifier.
- **FR-002**: The system MUST return the complete persisted command details for `GET /commands/{id}`.
- **FR-003**: The complete command details MUST include id, type, status, payload, response, error message, request received time, processing started time, and processing finished time.
- **FR-004**: The system MUST allow retrieving only the current status for a command by its identifier.
- **FR-005**: The status-only response MUST include only the command identifier and current status.
- **FR-006**: The system MUST allow listing commands filtered by status.
- **FR-007**: The list response MUST include command summary items, total matching count, current page, and page size.
- **FR-008**: Command summary items in list responses MUST include id, type, and status.
- **FR-009**: The system MUST support pagination for command listing.
- **FR-010**: The system MUST reject invalid command identifiers with a validation error.
- **FR-011**: The system MUST return a not-found error when a requested command does not exist.
- **FR-012**: The system MUST reject invalid status filters with a validation error.
- **FR-013**: The system MUST only return commands whose status matches the supplied status filter when a filter is provided.
- **FR-014**: The system MUST preserve and return persisted command response data when available.
- **FR-015**: The system MUST preserve and return persisted command error information when available.
- **FR-016**: The system MUST define explicit response and error contracts for command detail, status-only lookup, and command listing.

### Key Entities

- **Command**: Persisted command record with id, type, status, payload, optional response, optional error message, and lifecycle timestamps.
- **Command Status View**: Lightweight view containing only a command identifier and current status.
- **Command Summary**: List item containing a command identifier, command type, and current status.
- **Paginated Command List**: Collection of command summaries plus total count, page, and page size.

### Contracts

- **Command Detail Contract**: `GET /commands/{id}` returns the full persisted command record or a not-found error.
- **Command Status Contract**: `GET /commands/{id}/status` returns `{ "id": "...", "status": "..." }` or a not-found error.
- **Command List Contract**: `GET /commands` accepts status, page, and page size filters and returns `{ "items": [...], "total": n, "page": n, "page_size": n }`.
- **Status Values Contract**: Allowed status values are `queued`, `processing`, `completed`, and `failed`.

#### Command Detail Response Example

```json
{
  "id": "5f5f97c5-66f0-43f5-bf57-55f36f7a2f9f",
  "type": "SEND_EMAIL",
  "status": "completed",
  "payload": {
    "to": "aluno@ifes.edu.br"
  },
  "response": {
    "message_id": "12345"
  },
  "error_message": null,
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z"
}
```

#### Command Status Response Example

```json
{
  "id": "5f5f97c5-66f0-43f5-bf57-55f36f7a2f9f",
  "status": "processing"
}
```

#### Command List Response Example

```json
{
  "items": [
    {
      "id": "1",
      "type": "SEND_EMAIL",
      "status": "failed"
    },
    {
      "id": "2",
      "type": "GENERATE_REPORT",
      "status": "failed"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing commands can be retrieved by identifier while their records are retained.
- **SC-002**: 100% of detail lookups return all required persisted fields for the requested command.
- **SC-003**: 100% of status-only lookups return only the command identifier and status fields.
- **SC-004**: 100% of status-filtered list responses contain only commands matching the requested status.
- **SC-005**: Paginated list responses always include item count metadata with total, page, and page size.
- **SC-006**: 100% of unknown command lookups return a not-found outcome instead of an empty or misleading successful response.

## Assumptions

- Existing command records are already persisted and available through the command storage boundary.
- Command identifiers are globally unique and supplied by callers from prior command submission responses.
- The default list page is page 1 and the default page size is 20 when pagination parameters are omitted.
- Listing without a status filter may return commands across all statuses, while a supplied status filter restricts results to that status.
- Command listing returns summary records only, not full payloads or processing responses.
- Authentication and authorization rules are outside the scope of this feature.
