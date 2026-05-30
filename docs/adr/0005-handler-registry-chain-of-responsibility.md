# ADR-0005: Use Handler Registry and Chain of Responsibility Pipelines

## Status

Accepted

## Context

Each command type has different payload validation and business behavior. The
worker should not contain `if` or `match` logic for each command type, and new
types should be added without changing the main processing flow.

## Decision

Use a `HandlerRegistry` to map command type strings to command pipelines.

Each pipeline uses Chain of Responsibility:

- handlers receive a shared `CommandContext`;
- handlers can write metadata, errors, and result data;
- the pipeline stops when a handler records a blocking error;
- the worker only resolves and executes the pipeline.

The initial `TEST_COMMAND` pipeline contains validation, idempotency, business,
and audit handlers.

## Consequences

Positive:

- New command types can be added by creating a pipeline and registering it.
- Validation, idempotency, business logic, and audit behavior remain separated.
- The worker stays generic.

Tradeoffs:

- Handler order is important and must be tested.
- Shared context needs a clear contract so handlers do not rely on hidden state.
