# ADR-0008: Separate Command Detail, Status, and List Query Contracts

## Status

Accepted

## Context

External systems need different views of command state. Support workflows need
complete command records, polling workflows need only current status, and
monitoring workflows need paginated summaries filtered by status.

Using one response shape for all query workflows would either expose too much
data for polling and listing or withhold details needed for support.

## Decision

Expose three read-only command query contracts:

- `GET /commands/{id}` returns the complete persisted command record.
- `GET /commands/{id}/status` returns only `id` and `status`.
- `GET /commands` returns paginated summaries with `id`, `type`, and `status`,
  optionally filtered by command status.

Repository query behavior stays behind the `CommandRepository` port so Redis
and future storage adapters remain replaceable.

## Consequences

Positive:

- Clients can choose the smallest response needed for their workflow.
- Status polling avoids returning payloads and processing details.
- Monitoring lists remain compact and paginated.

Tradeoffs:

- The API has more query endpoints to document and test.
- Repository adapters must support both single-record reads and list queries.
