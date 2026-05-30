# Quickstart: Swagger and Code Documentation

## Start the Service

```bash
docker compose up --build
```

## Open API Documentation

Open the local interactive API documentation page:

```text
http://localhost:8000/docs
```

Verify:

- `POST /commands` is listed.
- Request schema shows `type` and `payload`.
- Success response includes `command_id` and `status`.
- Validation error response is documented.
- A valid `TEST_COMMAND` example is visible.

## Validate the Example

```bash
curl -i -X POST http://localhost:8000/commands \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_COMMAND","payload":{"message":"hello"}}'
```

Expected HTTP status:

```text
202 Accepted
```

## Run Documentation Tests

```bash
pytest
```

The test suite must verify:

- API docs and generated schema expose `POST /commands`;
- documented request and response examples match actual behavior;
- important command-processing modules have concise docstrings;
- external API documentation does not require clients to know queue implementation details.
