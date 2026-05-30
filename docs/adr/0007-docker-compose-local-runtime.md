# ADR-0007: Use Docker Compose for Local Runtime

## Status

Accepted

## Context

The project has multiple runtime processes: API, worker, Redis, and
RedisInsight. Developers need one repeatable command to run the complete local
environment.

## Decision

Use Docker Compose with services for:

- `api`: FastAPI served by Uvicorn.
- `worker`: Python worker process.
- `redis`: queue and runtime command store.
- `redisinsight`: local Redis inspection UI.

API and worker share the same Dockerfile and codebase. Runtime configuration is
provided through environment variables.

## Consequences

Positive:

- The complete asynchronous flow can be tested locally with one command.
- API and worker use the same application code.
- RedisInsight helps inspect queued messages and persisted command records.

Tradeoffs:

- Docker image builds are slower than running directly from the virtualenv.
- Compose is a local development tool, not a production deployment strategy.
