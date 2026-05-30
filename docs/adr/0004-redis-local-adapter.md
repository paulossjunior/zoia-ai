# ADR-0004: Use Redis as the Local Queue Adapter

## Status

Accepted

## Context

The service needs a local queue for asynchronous command processing. Earlier
versions also used Redis for runtime command records, but callback persistence
and audit requirements moved durable command state to PostgreSQL.

## Decision

Use Redis through the queue infrastructure adapter:

- `RedisCommandQueue` publishes and consumes JSON messages containing
  `command_id`.
- `RedisCommandRepository` remains only as a compatibility/local adapter; the
  default runtime command store is PostgreSQL.

Redis configuration comes from environment variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_QUEUE_NAME`

RedisInsight is included in Docker Compose for local queue inspection.

## Consequences

Positive:

- Queue messages can be inspected with RedisInsight.
- The same Redis service supports API and worker coordination.

Tradeoffs:

- Local development now runs PostgreSQL in addition to Redis.
- Redis remains replaceable because application logic depends only on
  `CommandQueue`.
