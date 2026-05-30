# ADR-0010: Operational Dashboard as a Read-Only Frontend

## Status

Accepted

## Context

Operators need a way to monitor persisted commands, processing outcomes,
callback outcomes, payloads, responses, and errors without interacting with the
command submission or worker flows.

The existing service already owns command persistence and asynchronous
processing. A monitoring dashboard must not introduce a second path for command
mutation or direct infrastructure access.

## Decision

Create a separate Vue 3 dashboard application under `dashboard/` and run it as
its own Docker Compose service. The dashboard consumes backend read endpoints:

- `GET /dashboard/indicators`
- `GET /dashboard/commands`
- `GET /dashboard/commands/{command_id}`

The dashboard is query-only. It does not access PostgreSQL or Redis directly,
does not submit commands, does not process queues, does not update statuses, and
does not execute or resend callbacks.

## Consequences

- Operational UI concerns stay isolated from the Python command service.
- Backend persistence remains the source of truth for command and callback
  state.
- New command types appear generically in the dashboard without worker-flow
  changes.
- Dashboard behavior can be tested with mocked read services and verified with
  Docker Compose.
- Large data sets still require backend pagination and filtering discipline.
