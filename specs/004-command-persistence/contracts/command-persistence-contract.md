# Contract: Command Persistence

## Persisted Command Record

Every accepted command must be persisted with this logical shape before it is queued:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "payload": {
    "message": "hello"
  },
  "status": "queued",
  "response": null,
  "error_message": null,
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": null,
  "processing_finished_at": null
}
```

## Successful Processing Record

When processing succeeds, the same command record must preserve payload and include the response when one is produced:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "payload": {
    "message": "hello"
  },
  "status": "completed",
  "response": {
    "echo": "hello"
  },
  "error_message": null,
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": "2026-05-30T19:00:01Z",
  "processing_finished_at": "2026-05-30T19:00:02Z"
}
```

## Failed Processing Record

When processing fails, the same command record must preserve payload and include the error:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "payload": {
    "message": "hello"
  },
  "status": "failed",
  "response": null,
  "error_message": "Handler execution failed: example",
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": "2026-05-30T19:00:01Z",
  "processing_finished_at": "2026-05-30T19:00:02Z"
}
```

## Complete Command Retrieval

```text
GET /commands/{command_id}
```

The complete retrieval contract returns the persisted execution record for the command identifier. It must include:

- command id;
- type;
- original payload;
- status;
- response;
- error message;
- request receipt timestamp;
- processing start timestamp;
- processing finish timestamp.

Unknown command:

Status: `404 Not Found`

```json
{
  "detail": "command not found"
}
```

## Contract Rules

- The record is created before queue publication.
- Queue publication does not remove or mutate the original payload.
- Processing updates must preserve the original payload.
- Successful processing stores `response` when produced and clears `error_message`.
- Failed processing stores `error_message` and clears `response`.
- The persisted record remains retrievable after final status is reached.
- Storage technology details are not part of this contract.
