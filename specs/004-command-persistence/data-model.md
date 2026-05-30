# Data Model: Command Persistence

## Entity: Command

Represents the persisted execution record for a command received by the system.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid string | Yes | Unique command identifier generated during submission |
| `type` | string | Yes | Command type used to select processing pipeline |
| `payload` | object | Yes | Original payload received during submission |
| `status` | enum | Yes | Current command lifecycle state |
| `response` | object or null | No | Structured processing response when success produces one |
| `error_message` | string or null | No | Clear failure message when processing fails |
| `request_received_at` | datetime | Yes | Timestamp when the command request was accepted |
| `processing_started_at` | datetime or null | No | Timestamp when worker processing started |
| `processing_finished_at` | datetime or null | No | Timestamp when processing completed or failed |

## Entity: Command Execution Record

External/support-facing view of the complete persisted command record.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | uuid string | Yes | Command identifier used for lookup |
| `type` | string | Yes | Command type |
| `payload` | object | Yes | Original payload |
| `status` | enum | Yes | Current lifecycle state |
| `response` | object or null | No | Persisted success response |
| `error_message` | string or null | No | Persisted failure message |
| `request_received_at` | datetime | Yes | Request receipt timestamp |
| `processing_started_at` | datetime or null | No | Processing start timestamp |
| `processing_finished_at` | datetime or null | No | Processing finish timestamp |

## Entity: Command Processing Response

Structured result captured from successful command processing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `response` | object | No | Handler-produced result; absent or null when no structured response is produced |

## Entity: Command Processing Error

Failure information captured from processing errors.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error_message` | string | Yes for failed commands | Clear failure reason, bounded to a safe length |

## Validation Rules

- `id` must be unique.
- `type` must be non-empty.
- `payload` must be an object and must remain unchanged after submission.
- `status` must be one of `queued`, `processing`, `completed`, or `failed`.
- `request_received_at` is set when the command is accepted.
- `processing_started_at` is set before business processing begins.
- `processing_finished_at` is set when processing completes or fails.
- `response` is present only when processing succeeds and a result is produced.
- `error_message` is present only when processing fails.
- Updating status or outcome must preserve id, type, payload, and request receipt time.

## State Transitions

```text
queued -> processing -> completed
queued -> processing -> failed
```

## Field Availability by Status

| Status | Payload | Response | Error Message | Request Received | Processing Started | Processing Finished |
|--------|---------|----------|---------------|------------------|--------------------|---------------------|
| `queued` | Present | Null | Null | Present | Null | Null |
| `processing` | Present | Null | Null | Present | Present | Null |
| `completed` | Present | Object or null | Null | Present | Present | Present |
| `failed` | Present | Null | Present | Present | Present or null | Present |
