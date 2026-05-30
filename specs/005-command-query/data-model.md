# Data Model: Command Query

## Entity: Command

Persisted command record available for full detail lookup.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid string | Yes | Unique command identifier |
| `type` | string | Yes | Command type |
| `status` | enum | Yes | Current command lifecycle state |
| `payload` | object | Yes | Original command payload |
| `response` | object or null | No | Processing response when available |
| `error_message` | string or null | No | Failure message when available |
| `request_received_at` | datetime | Yes | Time the command was accepted |
| `processing_started_at` | datetime or null | No | Time worker processing started |
| `processing_finished_at` | datetime or null | No | Time processing completed or failed |

## Entity: Command Status View

Lightweight response for status polling.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid string | Yes | Command identifier |
| `status` | enum | Yes | Current command lifecycle state |

## Entity: Command Summary

Compact list item for monitoring commands by status.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid string | Yes | Command identifier |
| `type` | string | Yes | Command type |
| `status` | enum | Yes | Current command lifecycle state |

## Entity: Paginated Command List

Response envelope for command list queries.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | array of Command Summary | Yes | Commands on the current page |
| `total` | integer | Yes | Total commands matching the filter |
| `page` | integer | Yes | Current page number |
| `page_size` | integer | Yes | Requested page size |

## Validation Rules

- `id` must be a valid command identifier for detail and status lookups.
- `status` filters must be one of `queued`, `processing`, `completed`, or `failed`.
- `page` must be greater than or equal to 1.
- `page_size` must be greater than or equal to 1.
- Default page is 1 when omitted.
- Default page size is 20 when omitted.
- List responses must include only summaries, not payloads, responses, or errors.
- Status-only responses must include only `id` and `status`.

## State Values

```text
queued
processing
completed
failed
```

## Relationships

- A Command produces one Command Status View for lightweight lookup.
- A Command produces one Command Summary when included in a paginated list.
- A Paginated Command List contains zero or more Command Summary items.
