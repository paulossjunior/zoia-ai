# Research: Command Query

## Decision: Split full detail lookup from status-only lookup

**Rationale**: The feature explicitly requires both full command details and lightweight status-only polling. Keeping separate application result contracts prevents status polling from exposing payloads, responses, or errors when the caller only needs lifecycle state.

**Alternatives considered**: Returning the same full record from both endpoints was rejected because it violates the status-only contract. Using query parameters on one endpoint was rejected because the requested API defines separate paths.

## Decision: Add query and list operations to the repository port

**Rationale**: Application use cases need to retrieve individual commands and list commands by status without depending on Redis. Extending the existing repository port keeps infrastructure replaceable and lets tests use in-memory storage.

**Alternatives considered**: Querying Redis directly from API routes was rejected because it violates infrastructure boundaries. Creating a separate read model adapter was considered but rejected for this increment because existing command records already contain the required fields.

## Decision: Return summary records for command lists

**Rationale**: The list endpoint is for monitoring command groups. Returning only id, type, and status keeps paginated responses small and avoids exposing payloads or processing details for many commands at once.

**Alternatives considered**: Returning full command records in list responses was rejected because it increases payload size and duplicates the full detail endpoint. Returning only ids was rejected because operators need type and status for useful monitoring.

## Decision: Use page/page_size pagination with deterministic ordering

**Rationale**: Pagination is required for large result sets. Page and page_size are straightforward for external systems and match the example contract. Ordering by request receipt time, newest first, gives predictable operational results.

**Alternatives considered**: Cursor pagination was considered but rejected for this small monitoring endpoint because the spec examples use page-based metadata. Unpaginated responses were rejected because they do not satisfy the acceptance criteria.

## Decision: Validate status values at the API/application boundary

**Rationale**: Allowed statuses are finite and already represented by the command status contract. Rejecting invalid filters prevents misleading empty results caused by misspelled statuses.

**Alternatives considered**: Treating unknown statuses as empty lists was rejected because it hides input errors. Allowing free-form statuses was rejected because command states are explicit.

## Decision: Keep query operations read-only and observable

**Rationale**: Query endpoints must not enqueue commands, consume queues, or execute handlers. Logs should record lookup/list activity and errors for operations visibility without logging sensitive payloads.

**Alternatives considered**: Reusing processing use cases for lookup was rejected because it risks side effects. Omitting logs was rejected because the constitution requires observable flows.
