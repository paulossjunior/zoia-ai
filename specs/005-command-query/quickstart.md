# Quickstart: Command Query

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

Save the returned command id.

## Retrieve Complete Command Details

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Expected shape:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "status": "completed",
  "payload": {
    "message": "hello"
  },
  "response": {
    "echo": "hello"
  },
  "error_message": null,
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z"
}
```

## Retrieve Status Only

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000/status
```

Expected shape:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "status": "completed"
}
```

## List Commands by Status

```bash
curl -i "http://localhost:8000/commands?status=failed&page=1&page_size=20"
```

Expected shape:

```json
{
  "items": [
    {
      "id": "00000000-0000-4000-8000-000000000000",
      "type": "TEST_COMMAND",
      "status": "failed"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

## Validate Errors

```bash
curl -i http://localhost:8000/commands/not-a-uuid
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000001
curl -i "http://localhost:8000/commands?status=unknown"
curl -i "http://localhost:8000/commands?page=0&page_size=20"
```

Expected outcomes:

- malformed ids return `400`;
- unknown commands return `404`;
- invalid status filters return `400`;
- invalid pagination returns `400`.

## Run Tests

```bash
pytest
```

The test suite must verify:

- full command detail lookup returns all persisted fields;
- status-only lookup returns only id and status;
- list filtering returns only matching statuses;
- list pagination returns page metadata;
- invalid ids, missing commands, invalid statuses, and invalid pagination are handled;
- query APIs do not enqueue commands or execute handlers.
