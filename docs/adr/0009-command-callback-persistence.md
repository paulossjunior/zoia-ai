# ADR 0009: Command Callback Persistence

## Status

Accepted

## Context

Commands now require durable traceability across submission, processing,
optional callback delivery, and later queries by command id or external business
id. Redis remains useful as a queue, but queue state is not a durable audit log.
Callback delivery is an external HTTP side effect and must not be coupled to the
domain model or command-specific handlers.

## Decision

Persist command records in PostgreSQL through `CommandRepository`, keep Redis as
the queue adapter through `CommandQueue`, and deliver callbacks through a
`CallbackClient` port implemented by infrastructure.

The command record stores the original payload, optional `external_id`, optional
callback URL, processing status, response payload, processing error, callback
status, callback error, retry count, and lifecycle timestamps.

Callback delivery is attempted only after processing reaches `completed` or
`failed`. Callback failure updates callback audit fields but does not change the
command processing status.

## Consequences

- Command history survives worker restarts and Redis queue churn.
- External systems can poll by command id or latest external id when callback is
  absent or fails.
- PostgreSQL, Redis, and HTTP client libraries remain infrastructure details.
- Adding new command types still requires only a new pipeline and registry entry.
