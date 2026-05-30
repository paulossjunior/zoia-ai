# Quickstart: Command Status Query

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

Expected response includes a command id:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "queued"
}
```

## Query Command Status

Replace the id with the value returned from submission:

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Expected successful shape:

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

## Validate Error Cases

Malformed id:

```bash
curl -i http://localhost:8000/commands/not-a-uuid
```

Expected status: `400 Bad Request`

Unknown id:

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Expected status when no command exists for that id: `404 Not Found`

## Open API Documentation

```text
http://localhost:8000/docs
```

Verify:

- `GET /commands/{command_id}` is listed.
- Success response includes command status fields.
- `400` invalid id and `404` not-found responses are documented.
- The response does not include the original command payload.

## Run Tests

```bash
pytest
```

The test suite must verify:

- status lookup for queued, processing, completed, and failed commands;
- malformed ids return `400`;
- unknown ids return `404`;
- lookup does not enqueue work or execute handlers;
- API documentation matches the runtime contract.
