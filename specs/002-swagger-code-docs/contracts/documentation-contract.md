# Documentation Contract: Swagger and Code Documentation

## Interactive API Documentation

The running service must expose an interactive API documentation page for local users.

Required documented operation:

- `POST /commands`

Required request documentation:

```json
{
  "type": "TEST_COMMAND",
  "payload": {
    "message": "hello"
  }
}
```

Required success response documentation:

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "queued"
}
```

Required validation error documentation:

```json
{
  "detail": "invalid command request"
}
```

Required response codes:

- `202`: command accepted for asynchronous processing
- `400`: invalid command submission

## Code Documentation Contract

The following areas must include concise documentation of responsibilities and extension points:

- command lifecycle entity and status values;
- command context shared by handlers;
- queue and repository ports;
- submit and process use cases;
- sequential command pipeline;
- handler registry and missing-pipeline behavior;
- API app, schemas, and route behavior;
- worker single-iteration and continuous loop behavior;
- `TEST_COMMAND` handlers and pipeline extension pattern.

## README Contract

README must include:

- local API documentation URL;
- example command submission matching the API docs;
- instructions to run tests;
- concise explanation of how to add a new command type;
- note that external clients do not need queue implementation knowledge.
