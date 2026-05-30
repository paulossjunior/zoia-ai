# Zoia AI - Async Command Processing

Python 3.12 service for asynchronous command processing. The HTTP API validates,
records, and queues commands; a separate worker consumes queued command IDs and
executes command-specific pipelines.

## Architecture

- `app/domain`: framework-free entities, statuses, contexts, handlers, and ports.
- `app/application`: use cases, pipeline executor, and handler registry.
- `app/infrastructure`: Redis queue adapter, PostgreSQL runtime repository,
  HTTP callback client, in-memory test repository, and logging.
- `app/api`: FastAPI/Pydantic HTTP boundary.
- `app/worker`: independent command consumer.
- `app/commands/test_command`: first Chain of Responsibility pipeline.

Redis, PostgreSQL, HTTP clients, FastAPI, and Docker do not appear in the domain layer.

Architecture Decision Records are available in [`docs/adr`](docs/adr/README.md).
Operational dashboard documentation is available in
[`docs/operational-dashboard.md`](docs/operational-dashboard.md).

## Local Python Setup

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Docker Compose

```bash
docker compose up --build
```

Services:

- `api`: `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`
- `worker`: `python -m app.worker.main`
- `redis`: Redis broker
- `redisinsight`: Redis UI at `http://localhost:5540`
- `postgres`: durable command store
- `dashboard`: read-only operational dashboard at `http://localhost:5173/dashboard`

In RedisInsight, add a database connection with host `redis` and port `6379`
when running from Docker Compose.

Environment variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_QUEUE_NAME`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `APP_ENV`
- `VITE_API_BASE_URL`
- `VITE_API_PROXY_TARGET`

## API Documentation

After the API service starts, open the interactive Swagger/OpenAPI
documentation:

```text
http://localhost:8000/docs
```

The generated schema is also available at:

```text
http://localhost:8000/openapi.json
```

Use the docs page to inspect `POST /commands`, the required `type` and
`payload` fields, optional `external_id` and `callback`, the `202` queued
acknowledgement, command queries, callback audit fields, and documented error
responses.

## Operational Dashboard

The local dashboard is a separate Vue 3 frontend that consumes read-only backend
contracts. It does not submit commands, consume queues, change statuses, modify
persisted records, or resend callbacks.

See [`docs/operational-dashboard.md`](docs/operational-dashboard.md) for the
full runtime, contract, validation, and maintenance notes.

With Docker Compose running, open:

```text
http://localhost:5173/dashboard
```

For frontend-only development:

```bash
cd dashboard
npm install
npm run dev
```

Dashboard read endpoints:

```text
GET /dashboard/indicators
GET /dashboard/commands
GET /dashboard/commands/{command_id}
```

The list endpoint supports pagination, filters, search, and sorting:

```bash
curl -i "http://localhost:8000/dashboard/commands?status=failed&page=1&page_size=20&sort_by=request_received_at&sort_direction=desc"
```

Run dashboard checks:

```bash
cd dashboard
npm test
npm run build
```

## Submit a Command

```bash
curl -i -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"}}'
```

With callback and external business id:

```bash
curl -i -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"},"external_id":"BOLSISTA-12345","callback":"https://sistema-origem.com/api/callback"}'
```

Expected response:

```json
{
  "command_id": "uuid",
  "status": "queued"
}
```

Invalid requests return HTTP 400 when `type` is missing/blank or `payload` is
missing/not an object.

## Retrieve Command Record

Use the command id returned by submission to query the read-only persisted
execution record:

```text
GET /commands/{command_id}
```

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Queued records preserve the original payload before worker processing starts:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "external_id": null,
  "callback": null,
  "payload": {
    "message": "hello"
  },
  "status": "queued",
  "response_payload": null,
  "error_message": null,
  "callback_status": "not_required",
  "callback_error_message": null,
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": null,
  "processing_finished_at": null,
  "callback_sent_at": null
}
```

Successful processed records include lifecycle fields and the produced
response when a handler writes one:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "external_id": "BOLSISTA-12345",
  "callback": "https://sistema-origem.com/api/callback",
  "payload": {
    "message": "hello"
  },
  "status": "completed",
  "response_payload": {
    "echo": "hello"
  },
  "error_message": null,
  "callback_status": "sent",
  "callback_error_message": null,
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": "2026-05-30T19:00:01Z",
  "processing_finished_at": "2026-05-30T19:00:02Z",
  "callback_sent_at": "2026-05-30T19:00:03Z"
}
```

Failed records keep the payload, clear the response, and persist the error:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "external_id": null,
  "callback": null,
  "payload": {
    "message": "hello"
  },
  "status": "failed",
  "response_payload": null,
  "error_message": "Handler execution failed: example",
  "callback_status": "not_required",
  "callback_error_message": null,
  "request_received_at": "2026-05-30T19:00:00Z",
  "processing_started_at": "2026-05-30T19:00:01Z",
  "processing_finished_at": "2026-05-30T19:00:02Z",
  "callback_sent_at": null
}
```

Malformed ids return HTTP 400:

```json
{
  "detail": "invalid command_id"
}
```

Unknown command ids return HTTP 404:

```json
{
  "detail": "command not found"
}
```

Command record lookup is read-only. It does not enqueue work, consume queue
messages, or run command handlers.

## Check Command Status Only

Use the status-only endpoint when a client needs to poll state without receiving
the full payload, response, error, or timestamps:

```text
GET /commands/{command_id}/status
```

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000/status
```

Expected response:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "processing",
  "callback_status": "pending"
}
```

## Retrieve Latest Command by External Id

When multiple commands share an external id, the latest command by
`request_received_at` is returned:

```text
GET /commands/external/{external_id}
```

```bash
curl -i http://localhost:8000/commands/external/BOLSISTA-12345
```

## List Commands

Use the list endpoint to monitor command groups by status with pagination:

```text
GET /commands?status=failed&page=1&page_size=20
```

```bash
curl -i "http://localhost:8000/commands?status=failed&page=1&page_size=20"
```

Expected response:

```json
{
  "items": [
    {
      "id": "1",
      "type": "SEND_EMAIL",
      "status": "failed"
    },
    {
      "id": "2",
      "type": "GENERATE_REPORT",
      "status": "failed"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

Invalid status filters return `{"detail":"invalid status"}`. Invalid
pagination returns `{"detail":"invalid pagination"}`.

## Worker Logs

The API stores accepted commands in PostgreSQL and publishes their IDs to the
Redis queue. The worker loads the command from PostgreSQL, runs the registered
pipeline, writes the final `completed` or `failed` status back to PostgreSQL,
and sends an optional callback after processing finishes. Callback failures set
`callback_status` to `failed` and preserve the command processing status and
`response_payload`. The service logs command submission, processing start,
processing success, processing failure, callback attempt, callback success, and
callback failure.

## Adding a Command Type

Create a new package under `app/commands/<command_name>/`, define handlers for
each processing responsibility, compose them in a command-specific pipeline
factory, then register that pipeline in `create_default_registry()`. Document
the payload contract in the new handlers or pipeline and keep the API route and
worker loop unchanged for new command types.

External clients do not need queue implementation knowledge. They only submit
the documented command envelope and track the returned command id; queue
implementation details remain internal and replaceable.

## Documentation Validation

Run the automated checks before changing command contracts or adding command
types:

```bash
pytest tests/test_documentation.py
pytest tests/test_architecture.py
pytest
```

Documentation should stay concise and focused on module responsibilities,
domain invariants, payload contracts, and extension points.
