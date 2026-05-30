# ADR-0001: Use Layered Domain-Oriented Architecture

## Status

Accepted

## Context

The service receives command submissions over HTTP, queues them, and processes
them in independent workers. The project constitution requires the domain to be
independent from FastAPI, Redis, Docker, databases, and other external
technologies.

Without clear boundaries, command lifecycle rules could become coupled to web
framework or queue details, making tests slower and future infrastructure
changes harder.

## Decision

Use a layered architecture:

- `app/domain`: command entity, status enum, context, handlers, and ports.
- `app/application`: use cases, registry, and pipeline orchestration.
- `app/infrastructure`: Redis adapters, in-memory repository, and logging.
- `app/api`: FastAPI and Pydantic HTTP boundary.
- `app/worker`: runtime loop that consumes queued command ids.
- `app/commands`: command-specific pipelines and handlers.

Domain code must not import infrastructure or framework modules.

## Consequences

Positive:

- Domain rules are testable without Redis, FastAPI, or Docker.
- Infrastructure can be replaced through adapters that implement ports.
- API and worker stay thin and delegate business flow to application use cases.

Tradeoffs:

- More files and interfaces are required than in a single-module prototype.
- Some simple operations need mapping between domain, application, and API
  contracts.
