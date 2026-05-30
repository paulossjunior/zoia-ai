# Research: Command Callback Persistence

## Decision: Use PostgreSQL as the command persistence adapter

**Rationale**: The feature explicitly requires command records to be retained, queryable, and auditable after processing. PostgreSQL provides durable storage, JSON fields for payloads and responses, indexes for command id and external id lookups, and predictable ordering for "most recent by external id" queries.

**Alternatives considered**: Continuing to use Redis as the runtime command store was rejected because the new requirement treats Redis as queue-only and PostgreSQL as persistence. In-memory storage remains useful for tests but is not suitable for runtime persistence.

## Decision: Keep Redis only for queueing command ids

**Rationale**: Redis is already integrated as the queue adapter. Keeping it as queue-only aligns with the restriction that Redis is an implementation detail for queueing while PostgreSQL stores the durable command record.

**Alternatives considered**: Using PostgreSQL as both queue and store was rejected for this increment because the current worker flow already uses a queue abstraction and Redis adapter. Mixing command state into queue messages was rejected because workers must load the persisted command before processing.

## Decision: Introduce a callback client port

**Rationale**: Callback delivery is an external HTTP side effect and must not leak into domain or application logic as a concrete HTTP client. A `CallbackClient` port lets the worker process use case trigger delivery while tests use fakes and infrastructure owns HTTP details.

**Alternatives considered**: Calling an HTTP library directly from the worker or use case was rejected because it couples application flow to infrastructure. Letting handlers perform callbacks was rejected because callback delivery is generic post-processing behavior, not command-specific business logic.

## Decision: Treat callback as optional and blank values as not provided

**Rationale**: The feature says callbacks occur only when the original callback field is present and filled. Treating null, missing, and blank values as not required avoids accidental outbound HTTP requests.

**Alternatives considered**: Requiring callback for all commands was rejected by the spec. Treating blank strings as pending callbacks was rejected because it would create invalid delivery attempts.

## Decision: Callback failures are audited separately from command processing status

**Rationale**: Callback delivery occurs after processing reaches `completed` or `failed`. A callback failure should set `callback_status=failed` and store a callback error message, but it must not change a successfully processed command into a failed command.

**Alternatives considered**: Marking the command failed when callback delivery fails was rejected because the processing outcome and notification outcome are separate concerns. Retrying silently without recording failure was rejected because errors cannot be silent.

## Decision: External id lookup returns the most recent command by receipt time

**Rationale**: `external_id` is not unique. Returning the most recent command gives source systems a deterministic answer for repeated submissions tied to the same business object.

**Alternatives considered**: Returning all commands for an external id was rejected because the feature specifically asks for the most recent command. Rejecting duplicate external ids was rejected because the spec says the field is not unique.

## Decision: Preserve Chain of Responsibility for command-specific processing

**Rationale**: The existing handler registry and pipeline pattern already supports command-specific validation, idempotency, business handling, and auditing. The callback feature should not add type-specific logic to the worker.

**Alternatives considered**: Adding type conditionals to the worker was rejected because it violates handler extensibility. Letting the API execute handlers was rejected because processing must remain asynchronous.
