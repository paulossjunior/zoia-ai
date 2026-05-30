# ADR-0003: Access Queue and Storage Through Ports

## Status

Accepted

## Context

The project currently uses Redis for local queueing and command persistence, but
Redis is an implementation detail. The domain and application flow should not be
rewritten if the queue or storage technology changes later.

## Decision

Define queue, repository, handler, and pipeline contracts in `app/domain/ports.py`.

Application use cases depend on these ports:

- `CommandQueue` publishes and consumes command ids.
- `CommandRepository` saves, reads, and updates command records.
- `CommandHandler` handles one responsibility in a pipeline.
- `CommandPipeline` executes a command context.

Infrastructure adapters implement these ports.

## Consequences

Positive:

- Redis can be replaced by another broker or database-backed adapter.
- Tests can use in-memory repositories and fake queues.
- The worker and API stay independent from concrete storage classes where
  practical.

Tradeoffs:

- Adapters must keep the port contract stable.
- Full-record serialization needs compatibility handling when contract fields
  evolve.
