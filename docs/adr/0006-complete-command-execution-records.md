# ADR-0006: Persist Complete Command Execution Records

## Status

Accepted

## Context

Operators and external integrators need traceability for every accepted command.
A status-only view is not enough to debug asynchronous processing because it
does not show the original payload, produced response, error message, or
lifecycle timestamps together.

## Decision

Persist a complete execution record for every valid command before queueing it.

The record includes:

- `id`
- `type`
- `payload`
- `status`
- `response`
- `error_message`
- `request_received_at`
- `processing_started_at`
- `processing_finished_at`

`GET /commands/{command_id}` returns the complete persisted record. Successful
processing stores `CommandContext.result` as `response`; failed processing
stores a clear `error_message` and clears `response`.

## Consequences

Positive:

- A single lookup gives support users the current status and execution history.
- Payload retention allows submitted data to be audited after processing.
- Success and failure outcomes are stored consistently.

Tradeoffs:

- Payloads may contain sensitive data, so future authorization and retention
  policies matter.
- The public retrieval contract exposes more operational data than a minimal
  status endpoint.
- Storage adapters need compatibility handling for timestamp field names.
