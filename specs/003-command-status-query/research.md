# Research: Command Status Query

## Decision: Add a read-only application use case for command status lookup

**Rationale**: The API should remain a delivery boundary and should not directly encode command retrieval behavior. A small application use case keeps status lookup consistent with the existing layered architecture and allows tests to validate that lookup is read-only.

**Alternatives considered**: Reading the repository directly inside the route was rejected because it would make the HTTP layer own application behavior. Adding behavior to the domain entity was rejected because lookup orchestration is an application concern.

## Decision: Reuse the existing CommandRepository port

**Rationale**: Command status already lives in stored command records. Reusing the repository port keeps Redis as an implementation detail and allows the same endpoint behavior to be tested with the in-memory repository.

**Alternatives considered**: Querying Redis directly from the API was rejected because it violates infrastructure abstraction. Adding a separate status store was rejected because it duplicates command lifecycle data and creates drift risk.

## Decision: Validate command identifiers before repository lookup

**Rationale**: The command submission flow generates UUID identifiers, so malformed ids should be rejected as client errors before lookup. This gives external clients clear feedback and avoids ambiguous "not found" responses for syntactically invalid ids.

**Alternatives considered**: Treating every unknown string as not found was rejected because it hides request mistakes. Accepting arbitrary ids was rejected because the public contract already defines command ids as generated unique identifiers.

## Decision: Return a public status view without payload

**Rationale**: Clients need lifecycle state, timestamps, type, and failure reason to monitor work. Returning the original payload is unnecessary for status monitoring and can expose submitted data unnecessarily.

**Alternatives considered**: Returning the full command record was rejected because it exposes payload data and couples the public response to the internal command entity. Returning only status was rejected because timestamps and error messages are needed to understand processing outcomes.

## Decision: Keep lookup independent from queue and handler execution

**Rationale**: Status lookup must be safe for polling. It must not publish queue messages, consume queue messages, invoke handlers, or alter command status.

**Alternatives considered**: Triggering processing when a queued command is queried was rejected because it would mix observation with execution and violate asynchronous worker ownership.

## Decision: Document the endpoint alongside command submission

**Rationale**: The status query completes the external asynchronous workflow: submit a command, receive an id, then query status. Keeping the contract in generated API docs and README reduces integration drift.

**Alternatives considered**: README-only documentation was rejected because generated API documentation already validates and exposes the service contract.
