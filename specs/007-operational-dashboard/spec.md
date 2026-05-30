# Feature Specification: Operational Command Dashboard

**Feature Branch**: `007-operational-dashboard`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Criar um Dashboard Operacional para monitoramento de comandos processados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Operational Indicators (Priority: P1)

As an operator or administrator, I want to open a dashboard and immediately see
the current operational health of command processing so that I can understand
volume, backlog, failures, and callback outcomes at a glance.

**Why this priority**: The dashboard's primary value is situational awareness.
Operators need summary indicators before they can decide whether to investigate
specific commands.

**Independent Test**: Can be tested by loading the dashboard with persisted
command records in different command and callback states, then verifying that
all indicators and distributions match those records and no command data is
modified.

**Acceptance Scenarios**:

1. **Given** persisted commands exist in queued, processing, completed, and failed states, **When** the operator opens the dashboard, **Then** the dashboard shows total commands and totals for each command status.
2. **Given** persisted commands have callback statuses of not required, pending, sent, and failed, **When** the operator opens the dashboard, **Then** the dashboard shows callback success and failure totals and callback status distribution.
3. **Given** there are no persisted commands, **When** the operator opens the dashboard, **Then** the dashboard shows the empty state message "O sistema não possui comandos registrados."
4. **Given** dashboard data is loading, **When** indicators have not yet loaded, **Then** the dashboard shows a visible loading state.
5. **Given** dashboard data cannot be loaded, **When** the loading attempt fails, **Then** the dashboard shows "Não foi possível carregar os dados."

---

### User Story 2 - Browse and Filter Commands (Priority: P2)

As an operator or administrator, I want to browse a paginated list of commands
and combine filters, sorting, and search criteria so that I can locate relevant
records quickly during operational analysis.

**Why this priority**: After seeing indicators, operators need an efficient way
to narrow down persisted records by status, type, external id, dates, callback
status, and identifiers.

**Independent Test**: Can be tested by creating persisted command records with
different statuses, types, external ids, callback statuses, and timestamps, then
applying filters, sorting, pagination, and searches and verifying only matching
records are shown in the expected order.

**Acceptance Scenarios**:

1. **Given** persisted command records exist, **When** the operator views the command list, **Then** the table shows Command ID, Type, External ID, Status, Callback Status, receipt date, and finish date.
2. **Given** many command records exist, **When** the operator opens the list, **Then** the most recent records are shown first and pagination is available.
3. **Given** the operator applies filters for status, type, external id, receipt period, processing period, and callback status, **When** the list is refreshed, **Then** only commands matching all selected filters are shown.
4. **Given** the operator sorts by receipt date, processing start date, finish date, status, or type, **When** the sort is applied, **Then** the list order changes according to the selected field and direction.
5. **Given** the operator searches by Command ID, **When** a matching command exists, **Then** the matching command is shown.
6. **Given** the operator searches by External ID, **When** one or more matching commands exist, **Then** the matching commands are shown.

---

### User Story 3 - Inspect Command Details (Priority: P3)

As an operator or administrator, I want to select a command and inspect its full
details so that I can understand what was submitted, what happened during
processing, what response was produced, and whether callback delivery succeeded
or failed.

**Why this priority**: Detail inspection completes the monitoring flow by
allowing operators to move from summary indicators and filtered lists into a
single command's complete audit record.

**Independent Test**: Can be tested by selecting a known persisted command and
verifying that identification, processing, callback, payload, response, and
error sections exactly match the persisted record.

**Acceptance Scenarios**:

1. **Given** a command is visible in the list, **When** the operator selects it, **Then** a details view shows Command ID, Type, and External ID.
2. **Given** the selected command has processing timestamps, **When** details are shown, **Then** status, receipt date, processing start date, and finish date are visible.
3. **Given** the selected command has callback data, **When** details are shown, **Then** callback URL, callback status, callback error message, and callback sent date are visible.
4. **Given** the selected command has original payload data, **When** details are shown, **Then** the payload is displayed as readable formatted JSON.
5. **Given** the selected command has a response payload, **When** details are shown, **Then** the response is displayed as readable formatted JSON.
6. **Given** the selected command has an error message, **When** details are shown, **Then** the error message is visible.

---

### User Story 4 - Refresh Dashboard Data (Priority: P4)

As an operator or administrator, I want to manually refresh dashboard data
without reloading the whole page so that I can update indicators and lists while
preserving my working context.

**Why this priority**: Manual refresh supports near-real-time operational use
while keeping the first version simple and explicitly controlled by the user.

**Independent Test**: Can be tested by changing persisted command records after
the dashboard loads, triggering manual refresh, and verifying indicators and
list data update without data mutation.

**Acceptance Scenarios**:

1. **Given** the dashboard is showing indicators and a command list, **When** the operator triggers manual refresh, **Then** indicators are reloaded.
2. **Given** filters or pagination are currently applied, **When** the operator triggers manual refresh, **Then** the list reloads using the current criteria.
3. **Given** refresh fails, **When** the dashboard cannot load fresh data, **Then** the dashboard shows "Não foi possível carregar os dados." without clearing already visible data unnecessarily.

### Edge Cases

- No command records exist.
- Matching filters return no records.
- Search by Command ID has no match.
- Search by External ID has no match.
- A command is still queued and has no processing start or finish date.
- A command is processing and has no finish date.
- A command has no external id.
- A command has no callback URL and callback status is not required.
- A command has callback failure details but a successful processing result.
- Payload or response is empty, null, deeply nested, or contains arrays.
- Loading indicators succeeds while list loading fails, or the list succeeds while details loading fails.
- The operator refreshes while a previous load is still in progress.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a read-only operational dashboard for operators and administrators.
- **FR-002**: The dashboard MUST show total commands.
- **FR-003**: The dashboard MUST show totals for queued, processing, completed, and failed commands.
- **FR-004**: The dashboard MUST show total callbacks sent successfully.
- **FR-005**: The dashboard MUST show total callbacks with failure.
- **FR-006**: The dashboard MUST show command distribution by status: queued, processing, completed, and failed.
- **FR-007**: The dashboard MUST show callback distribution by status: not required, pending, sent, and failed.
- **FR-008**: Dashboard indicators MUST reflect only persisted command records.
- **FR-009**: The dashboard MUST show a paginated command table.
- **FR-010**: The command table MUST show Command ID, Type, External ID, Status, Callback Status, receipt date, and finish date.
- **FR-011**: The command table MUST show the most recent records first by default.
- **FR-012**: The command table MUST support filtering by command status.
- **FR-013**: The command table MUST support filtering by command type.
- **FR-014**: The command table MUST support filtering by external id.
- **FR-015**: The command table MUST support filtering by receipt period.
- **FR-016**: The command table MUST support filtering by processing period.
- **FR-017**: The command table MUST support filtering by callback status.
- **FR-018**: The dashboard MUST allow multiple filters to be combined.
- **FR-019**: The command table MUST support ordering by receipt date, processing start date, finish date, status, and type.
- **FR-020**: The dashboard MUST support search by Command ID.
- **FR-021**: The dashboard MUST support search by External ID.
- **FR-022**: The dashboard MUST provide a details view for a selected command.
- **FR-023**: The details view MUST show command identification: Command ID, Type, and External ID.
- **FR-024**: The details view MUST show processing information: status, receipt date, processing start date, and finish date.
- **FR-025**: The details view MUST show callback information: callback URL, callback status, callback error message, and callback sent date.
- **FR-026**: The details view MUST show the original payload as formatted JSON.
- **FR-027**: The details view MUST show response payload as formatted JSON when present.
- **FR-028**: The details view MUST show command error message when present.
- **FR-029**: JSON views MUST format JSON automatically in a readable structure.
- **FR-030**: JSON views MUST allow nested objects and arrays to be expanded and collapsed.
- **FR-031**: JSON views MUST visually distinguish hierarchy levels.
- **FR-032**: The dashboard MUST show "O sistema não possui comandos registrados." when there are no command records.
- **FR-033**: The dashboard MUST show "Não foi possível carregar os dados." when dashboard data cannot be loaded.
- **FR-034**: The dashboard MUST show a visual loading indicator while data is being loaded.
- **FR-035**: The dashboard MUST allow manual refresh of indicators and command lists without reloading the page.
- **FR-036**: The dashboard MUST be read-only and MUST NOT process commands.
- **FR-037**: The dashboard MUST NOT process queues.
- **FR-038**: The dashboard MUST NOT alter command status.
- **FR-039**: The dashboard MUST NOT modify persisted command records.
- **FR-040**: The dashboard MUST NOT execute or resend callbacks.
- **FR-041**: The dashboard MUST read only information already persisted by the platform.

### Key Entities

- **Dashboard Metrics**: Aggregated operational counts for commands and callbacks by lifecycle status.
- **Command List Item**: Summary row for a persisted command containing identifiers, statuses, and key timestamps.
- **Command Detail**: Complete read-only view of one persisted command, including payload, response, errors, callback data, and timestamps.
- **Dashboard Filter**: User-selected criteria used to narrow command list results by status, type, external id, periods, callback status, or search text.
- **JSON Viewer State**: Presentation state controlling whether nested payload or response structures are expanded or collapsed.

### Contracts

- **Dashboard Metrics Contract**: Returns total commands, command counts by status, callback success and failure totals, and callback counts by status.
- **Command List Contract**: Accepts pagination, filters, sorting, and search criteria; returns command list items ordered by the requested criteria and total result count.
- **Command Detail Contract**: Accepts a command identifier and returns the complete persisted command record for display.
- **Dashboard Error Contract**: Represents loading failures with the user-facing message "Não foi possível carregar os dados."
- **Empty State Contract**: Represents no available records with the user-facing message "O sistema não possui comandos registrados."

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can see total command and callback status indicators within one dashboard view.
- **SC-002**: Operators can identify commands in any supported command status using filters in under 30 seconds during validation.
- **SC-003**: Operators can locate a known command by Command ID or External ID in under 30 seconds during validation.
- **SC-004**: Operators can open a command details view and verify payload, response, error, callback data, and timestamps without navigating away from the dashboard flow.
- **SC-005**: 100% of dashboard interactions are read-only and leave persisted command records unchanged.
- **SC-006**: 100% of loading, empty, and load-error states show the specified user-facing messages or visual loading indicator.
- **SC-007**: JSON payload and response views preserve valid JSON structure while making nested objects and arrays readable through expand/collapse controls.
- **SC-008**: Manual refresh updates indicators and list data using the current dashboard criteria without a full page reload.

## Assumptions

- Operators and administrators are authorized users; authentication and role management are outside this feature's scope unless defined by a later feature.
- The dashboard is intended for operational monitoring, not command remediation or replay.
- The first version uses manual refresh only; automatic live updates can be specified later.
- The dashboard displays data already retained by the command persistence feature.
- Date filters use the persisted receipt, processing start, and processing finish timestamps.
- Search by Command ID is exact-match oriented, while search by External ID may return multiple records.
- Very large result sets are handled through pagination rather than loading all records at once.
