# ADR-0002: Process Commands Asynchronously

## Status

Accepted

## Context

External systems submit commands that may require slow or failure-prone
business processing. HTTP clients should not wait for command-specific handlers
to finish, and the API must not execute heavy work during the request.

The system still needs immediate traceability after accepting a command.

## Decision

The HTTP API validates the command envelope, persists a queued command record,
publishes the command id to a queue, and returns `202 Accepted` with:

```json
{
  "command_id": "uuid",
  "status": "queued"
}
```

Independent workers consume queued command ids, load the command record, resolve
the pipeline by command type, execute handlers, and persist the final outcome.

## Consequences

Positive:

- HTTP responses are fast and do not depend on business handler latency.
- Workers can scale independently from the API.
- Processing errors are isolated from command submission.

Tradeoffs:

- Clients need to query command status or execution records after submission.
- Queue and repository consistency must be carefully maintained.
