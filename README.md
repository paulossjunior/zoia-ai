# Zoia AI - Async Command Processing

Python 3.12 service for asynchronous command processing. The HTTP API validates,
records, and queues commands; a separate worker consumes queued command IDs and
executes command-specific pipelines.

## Architecture

- `app/domain`: framework-free entities, statuses, contexts, handlers, and ports.
- `app/application`: use cases, pipeline executor, and handler registry.
- `app/infrastructure`: Redis queue adapter, Redis-backed runtime repository,
  in-memory test repository, and logging.
- `app/api`: FastAPI/Pydantic HTTP boundary.
- `app/worker`: independent command consumer.
- `app/commands/test_command`: first Chain of Responsibility pipeline.

Redis, FastAPI, and Docker do not appear in the domain layer.

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

Environment variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_QUEUE_NAME`
- `APP_ENV`

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
`payload` fields, the `202` queued acknowledgement, and the `400` validation
error response.

## Submit a Command

```bash
curl -i -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"}}'
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

## Check Command Status

Use the command id returned by submission to query the read-only status view:

```text
GET /commands/{command_id}
```

```bash
curl -i http://localhost:8000/commands/00000000-0000-4000-8000-000000000000
```

Successful responses include lifecycle fields and never include the original
command payload:

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

Status lookup is read-only. It does not enqueue work, consume queue messages, or
run command handlers.

## Worker Logs

The API stores accepted commands in Redis and publishes their IDs to the Redis
queue. The worker loads the command from Redis, runs the registered pipeline,
and writes the final `completed` or `failed` status back to Redis. The service
logs command submission, processing start, processing success, and processing
failure.

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
