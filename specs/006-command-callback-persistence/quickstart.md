# Quickstart: Command Callback Persistence

## Start the Service

```bash
docker compose up --build
```

The local environment should include:

- API service;
- worker service;
- Redis for queueing;
- PostgreSQL for command persistence;
- RedisInsight for queue inspection.

## Submit a Command Without Callback

```bash
curl -s -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"}}'
```

Expected response:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "queued"
}
```

The persisted command should have `callback_status` set to `not_required`, and
no external HTTP callback should be attempted.

## Submit a Command With Callback

```bash
curl -s -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TEST_COMMAND",
    "payload": {"message": "hello"},
    "external_id": "BOLSISTA-12345",
    "callback": "https://sistema-origem.com/api/callback"
  }'
```

The persisted command should have:

```json
{
  "external_id": "BOLSISTA-12345",
  "callback": "https://sistema-origem.com/api/callback",
  "status": "queued",
  "callback_status": "pending"
}
```

## Retrieve Command Details

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

The response includes submission data, processing status, response or error,
callback audit fields, and timestamps.

## Retrieve Status Only

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000/status
```

Expected shape:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "processing",
  "callback_status": "pending"
}
```

## Retrieve by External Id

```bash
curl -i http://localhost:8000/commands/external/BOLSISTA-12345
```

When multiple commands share the same external id, the response should be the
most recent command by request receipt time.

## Validate Callback Failure Behavior

Use a callback URL that returns an error or is unreachable. After processing:

- command processing status remains `completed` when processing succeeded;
- `response_payload` remains available;
- `callback_status` becomes `failed`;
- `callback_error_message` records the delivery failure.

## Run Tests

```bash
pytest
```

The suite must verify:

- valid and invalid submissions;
- persistence before queue publication;
- PostgreSQL persistence of JSON payloads and outcomes;
- worker success and failure status transitions;
- callback sent, not required, and failed flows;
- callback failures do not change processing status;
- command lookup by id, status lookup, and latest external id lookup;
- API submission never executes command handlers directly.
