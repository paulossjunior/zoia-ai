# Research: Async Command Processing

## Decision: Python 3.12 service with FastAPI and Pydantic at the HTTP boundary

**Rationale**: The copied implementation context explicitly selects Python 3.12, FastAPI, and Pydantic. FastAPI provides a small HTTP surface for `POST /commands`, while Pydantic is restricted to request/response validation in `app/api` so domain code remains framework-free.

**Alternatives considered**: Flask or bare ASGI were not chosen because FastAPI/Pydantic is the requested stack and provides clearer request validation with less boilerplate.

## Decision: Redis as queue broker behind `CommandQueue`

**Rationale**: Redis is required as the queue implementation, but the constitution states infrastructure must be replaceable. The application will depend on a `CommandQueue` port; `RedisCommandQueue` will serialize messages as JSON and publish/consume command identifiers.

**Alternatives considered**: Direct Redis usage in use cases was rejected because it would couple application behavior to infrastructure. In-process queues were rejected because the requested runtime includes independent API and worker processes.

## Decision: In-memory command repository for v1 behind `CommandRepository`

**Rationale**: The copied implementation context allows an initial in-memory repository. This lets the v1 prove asynchronous flow, status transitions, and handler execution while keeping a clear replacement path for PostgreSQL.

**Alternatives considered**: PostgreSQL was deferred because it is not required for v1. Redis-backed persistence was rejected because Redis is designated as queue broker and persistence should remain separately abstracted.

## Decision: Worker resolves pipelines through `HandlerRegistry`

**Rationale**: The worker must not contain command-type-specific logic. A registry maps each command `type` to a `CommandPipeline`, keeping the worker generic and making new command types additive.

**Alternatives considered**: A `switch`/`if` chain in the worker was rejected because it violates extensibility. Dynamic module discovery was deferred to avoid unnecessary complexity in v1.

## Decision: Chain of Responsibility per command pipeline

**Rationale**: Each command type may need its own validation, idempotency, business action, and audit behavior. A shared `CommandContext` lets handlers communicate metadata, errors, and results while preserving handler order and interruption semantics.

**Alternatives considered**: A single monolithic command handler was rejected because it makes validation, idempotency, business behavior, and audit hard to test independently.

## Decision: Docker Compose local topology

**Rationale**: The requested environment has `api`, `worker`, and `redis` services. API and worker share the same image/codebase but run different commands, matching the asynchronous boundary.

**Alternatives considered**: Running worker inside the API process was rejected because command processing must be independent from HTTP request handling.
