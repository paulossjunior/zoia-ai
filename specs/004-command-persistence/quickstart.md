# Quickstart: Command Persistence

## Start the Service

```bash
docker compose up --build
```

## Submit a Command

```bash
curl -s -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"}}'
```

The response includes a command id:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "queued"
}
```

## Retrieve the Complete Command Record

Replace the id with the value returned during submission:

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Expected record shape after successful processing:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
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

## Validate Failed Processing

Submit a command whose handler validation fails or use a test fixture that raises from a handler. The retrieved record should show:

```json
{
  "status": "failed",
  "response": null,
  "error_message": "clear failure message"
}
```

## Inspect Local Persistence

RedisInsight is available at:

```text
http://localhost:5540
```

When running from Docker Compose, connect to host `redis` on port `6379`.

## Run Tests

```bash
pytest
```

The test suite must verify:

- commands are persisted before queue publication;
- payload remains available after status updates;
- processing start and finish timestamps are stored;
- success responses are persisted;
- failure error messages are persisted;
- complete records can be retrieved by command id;
- API submission still does not execute command processing directly.
