# Data Model: Command Status Query

## Entity: Command Status View

Represents the public, read-only view returned when a client queries a command by id.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | uuid string | Yes | Identifier returned by command submission |
| `type` | string | Yes | Command type originally submitted |
| `status` | enum | Yes | Current command lifecycle state |
| `created_at` | datetime string | Yes | When the command was accepted |
| `started_at` | datetime string or null | No | When worker processing started |
| `completed_at` | datetime string or null | No | When processing ended successfully or failed |
| `error_message` | string or null | No | Failure reason when status is `failed` |

## Entity: Command Identifier

Represents the client-provided path value used to find a command.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | uuid string | Yes | Must be syntactically valid and correspond to a stored command for success |

## Entity: Status Lookup Error

Represents public error responses for failed status lookups.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `detail` | string | Yes | Concise reason such as `invalid command_id` or `command not found` |

## Validation Rules

- `command_id` must be a valid UUID string.
- A valid UUID that does not correspond to a stored command returns not found.
- Status must be one of `queued`, `processing`, `completed`, or `failed`.
- `queued` commands have null `started_at`, null `completed_at`, and null `error_message`.
- `processing` commands have non-null `started_at`, null `completed_at`, and null `error_message`.
- `completed` commands have non-null `completed_at` and null `error_message`.
- `failed` commands have non-null `completed_at` and non-empty `error_message`.
- The status view does not include the original command payload.

## State Transitions Observed

```text
queued -> processing -> completed
queued -> processing -> failed
```

The status query observes these states but does not cause transitions.
