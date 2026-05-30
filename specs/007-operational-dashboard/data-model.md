# Data Model: Operational Command Dashboard

## Entity: DashboardIndicators

Read-only operational metrics displayed in indicator cards.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total_commands` | number | Yes | Total persisted commands |
| `queued_commands` | number | Yes | Commands currently queued |
| `processing_commands` | number | Yes | Commands currently processing |
| `completed_commands` | number | Yes | Commands completed successfully |
| `failed_commands` | number | Yes | Commands failed during processing |
| `callback_not_required` | number | Yes | Commands with no callback required |
| `callback_pending` | number | Yes | Commands awaiting callback delivery |
| `callback_sent` | number | Yes | Commands with callback sent successfully |
| `callback_failed` | number | Yes | Commands with callback delivery failure |

## Entity: CommandListItem

Summary row displayed in the dashboard command table.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | string | Yes | Unique command identifier |
| `type` | string | Yes | Command type |
| `external_id` | string or null | No | Source-system business identifier |
| `status` | CommandStatus | Yes | Command processing status |
| `callback_status` | CallbackStatus | Yes | Callback delivery status |
| `request_received_at` | datetime | Yes | Command receipt timestamp |
| `processing_finished_at` | datetime or null | No | Processing finish timestamp |

## Entity: CommandDetail

Complete command detail record displayed in a drawer or modal.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | string | Yes | Unique command identifier |
| `type` | string | Yes | Command type |
| `external_id` | string or null | No | Source-system business identifier |
| `status` | CommandStatus | Yes | Command processing status |
| `request_received_at` | datetime | Yes | Command receipt timestamp |
| `processing_started_at` | datetime or null | No | Processing start timestamp |
| `processing_finished_at` | datetime or null | No | Processing finish timestamp |
| `callback` | string or null | No | Callback URL from the original command |
| `callback_status` | CallbackStatus | Yes | Callback delivery status |
| `callback_error_message` | string or null | No | Callback failure message |
| `callback_sent_at` | datetime or null | No | Callback success timestamp |
| `payload` | object or null | No | Original command payload |
| `response_payload` | object or null | No | Processing response payload |
| `error_message` | string or null | No | Processing failure message |

## Entity: DashboardFilters

Criteria sent to the backend when loading the command list.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | CommandStatus or null | No | Filter by command status |
| `type` | string or null | No | Filter by command type |
| `external_id` | string or null | No | Filter by external id |
| `callback_status` | CallbackStatus or null | No | Filter by callback status |
| `received_from` | datetime or null | No | Start of receipt period |
| `received_to` | datetime or null | No | End of receipt period |
| `processing_from` | datetime or null | No | Start of processing period |
| `processing_to` | datetime or null | No | End of processing period |
| `search` | string or null | No | Search text for command id or external id |

## Entity: Pagination

Pagination metadata and selected page state.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `page` | number | Yes | Current page, starting at 1 |
| `page_size` | number | Yes | Number of rows requested per page |
| `total` | number | Yes | Total records matching criteria |

## Entity: Sorting

Current table ordering.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sort_by` | SortField | Yes | Selected sortable field |
| `sort_direction` | `asc` or `desc` | Yes | Sort direction |

## Entity: DashboardState

Store state used to coordinate dashboard components.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `indicators` | DashboardIndicators or null | No | Loaded indicator data |
| `commands` | CommandListItem[] | Yes | Current table rows |
| `filters` | DashboardFilters | Yes | Current list filters |
| `pagination` | Pagination | Yes | Current pagination metadata |
| `sorting` | Sorting | Yes | Current sort configuration |
| `selected_command` | CommandDetail or null | No | Detail record selected by the operator |
| `is_loading_indicators` | boolean | Yes | Indicator loading state |
| `is_loading_commands` | boolean | Yes | List loading state |
| `is_loading_details` | boolean | Yes | Detail loading state |
| `error_message` | string or null | No | Current user-facing error message |

## Value Sets

### CommandStatus

```text
queued
processing
completed
failed
```

### CallbackStatus

```text
not_required
pending
sent
failed
```

### SortField

```text
request_received_at
processing_started_at
processing_finished_at
status
type
```

## Validation Rules

- `page` must be greater than or equal to 1.
- `page_size` must be greater than 0.
- `status`, when present, must be one of the allowed command statuses.
- `callback_status`, when present, must be one of the allowed callback statuses.
- `sort_by` must be one of the allowed sort fields.
- `sort_direction` must be `asc` or `desc`.
- Date period filters may be omitted independently.
- Search text may represent a command id or an external id.
- Empty responses must show the empty state rather than a broken table.
- Null payloads and response payloads must render explicitly as null or empty JSON values.

## State Transitions

Dashboard UI state:

```text
idle -> loading -> loaded
idle -> loading -> error
loaded -> refreshing -> loaded
loaded -> refreshing -> error
loaded -> details_loading -> details_loaded
loaded -> details_loading -> error
```

The dashboard must not cause command lifecycle transitions.
