# Quickstart: Async Command Processing

## Prerequisites

- Docker and Docker Compose
- Python 3.12 if running tests outside containers

## Environment Variables

The local Docker Compose setup must provide:

```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_QUEUE_NAME=commands
APP_ENV=local
```

## Run Locally

```bash
docker compose up --build
```

Expected services:

- `api`: runs `uvicorn app.api.main:app`
- `worker`: runs `python -m app.worker.main`
- `redis`: queue broker

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

The HTTP status must be `202 Accepted`.

## Validate Asynchronous Processing

After submitting a valid `TEST_COMMAND`, inspect worker logs:

```bash
docker compose logs worker
```

Expected observations:

- submission log from the API path;
- worker start log when the command is consumed;
- handler execution through the registered `TEST_COMMAND` pipeline;
- success log with final `completed` status, or failure log with final `failed` status.

## Run Tests

```bash
pytest
```

The test suite must cover:

- `POST /commands` success and validation failures;
- submit use case persistence-before-queue behavior;
- process use case status transitions and registry resolution;
- worker consumption flow;
- Chain of Responsibility ordering, interruption, shared context, and handler failure behavior;
- architecture constraints that keep FastAPI, Redis, and Docker out of the domain layer.
