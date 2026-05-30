# Research: Command Persistence

## Decision: Extend the existing Command entity as the persisted execution record

**Rationale**: The current command entity already owns id, type, payload, status, timestamps, and error fields. Extending it with a response field and explicit lifecycle timestamp names keeps the persisted record aligned with the domain model without creating a parallel history object.

**Alternatives considered**: A separate command history entity was rejected for this feature because the requested history is the complete latest execution record for one command, not a multi-event audit log. A separate response store was rejected because it would split one command's traceability across multiple records.

## Decision: Preserve existing timestamps while aligning names to the persistence contract

**Rationale**: Existing code already tracks `created_at`, `started_at`, and `completed_at`. The feature contract names these concepts `request_received_at`, `processing_started_at`, and `processing_finished_at`. The implementation should provide the external/persisted contract names while avoiding unnecessary loss of compatibility with current status lookup behavior.

**Alternatives considered**: Renaming every internal field immediately was considered but may create broad churn across tests and adapters. Keeping only the old names was rejected because the requested persisted contract explicitly names receipt/start/finish timestamps.

## Decision: Persist handler context result as the command response on success

**Rationale**: Pipelines already share a `CommandContext` with a `result` field. Capturing that result on successful processing gives every command type a generic way to persist a response without the worker knowing command-specific handler internals.

**Alternatives considered**: Requiring handlers to write directly to storage was rejected because it couples business handlers to persistence. Returning a separate response object from every handler was rejected because the existing Chain of Responsibility already provides a shared result location.

## Decision: Keep payload retention through repository update operations

**Rationale**: Status updates and processing outcomes must not erase the original payload. Repository adapters should serialize and update the whole command record consistently so payload, response, error, and timestamps stay tied to the same id.

**Alternatives considered**: Storing only status deltas was rejected because complete retrieval must include payload and processing outcome. Mutating partial fields in the adapter was rejected for the initial implementation because full-record serialization is simpler and already matches the current repository pattern.

## Decision: Provide complete command record retrieval separately from lightweight status semantics

**Rationale**: The existing status query intentionally avoids returning payload. This feature requires complete execution record retrieval for audit/support workflows. The implementation should preserve the status view while adding or extending a contract that returns the full persisted record where appropriate.

**Alternatives considered**: Adding payload to the status response was rejected because it would break the privacy-conscious status contract established earlier. Creating only internal retrieval with no public contract was rejected because the spec requires later recovery by command id.

## Decision: Continue using Redis as the local runtime adapter behind CommandRepository

**Rationale**: The current architecture already abstracts storage through `CommandRepository`, and Redis-backed storage exists. The feature can improve durability semantics within the current adapter while keeping storage replaceable for a future database.

**Alternatives considered**: Introducing a new database in this feature was rejected because the user requested persistence behavior and traceability, not a specific storage migration. In-memory-only persistence was rejected for runtime use because records would disappear on process restart.
