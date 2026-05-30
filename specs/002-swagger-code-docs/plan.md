# Implementation Plan: Swagger and Code Documentation

**Branch**: `002-swagger-code-docs` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-swagger-code-docs/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Improve discoverability and maintainability of the asynchronous command service by enhancing the interactive API documentation for `POST /commands`, aligning request/response/error examples with actual runtime behavior, and adding concise code documentation at the domain, application, infrastructure, API, worker, and command pipeline boundaries. The feature should make the command submission contract understandable to external integrators and make extension points clear for developers adding future command types.

## Technical Context

**Language/Version**: Python 3.12 target runtime; current local tests may execute with the active virtualenv interpreter  
**Primary Dependencies**: Existing FastAPI/Pydantic/OpenAPI documentation support; no new runtime dependency required  
**Storage**: N/A for documentation changes; existing command storage behavior remains unchanged  
**Testing**: Pytest with FastAPI TestClient and documentation/source inspection tests  
**Target Platform**: Existing Docker Compose local environment with API, worker, and Redis  
**Project Type**: Web service plus worker  
**Performance Goals**: API documentation page should be reachable within 1 minute after local service startup; documentation tests should run as part of the normal pytest suite  
**Constraints**: Documentation must not expose queue implementation details as external client requirements; domain code must remain free of infrastructure and framework dependencies; comments/docstrings must stay concise and explain responsibilities or invariants rather than restating code  
**Scale/Scope**: Covers the existing `POST /commands` operation, current command-processing source modules, README local docs, and extension guidance for future command types

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. Documentation updates in domain modules will describe domain responsibilities without importing or referencing infrastructure APIs as dependencies.
- **Asynchronous command flow**: PASS. API docs will clarify that HTTP submission validates, records, queues, and returns acknowledgement while worker processing happens independently.
- **Explicit contracts**: PASS. OpenAPI/interactive docs will expose request, response, validation errors, examples, and state values for `POST /commands`.
- **Infrastructure abstraction**: PASS. Public API documentation will avoid requiring external clients to know Redis or repository implementation details.
- **Observability**: PASS. Developer documentation will preserve status/logging expectations for submission, processing start, success, and failure.
- **Testing discipline**: PASS. Tests will verify docs availability, schema/example alignment, code documentation presence, README references, and domain architecture constraints.
- **Handler extensibility**: PASS. Handler registry and command pipeline documentation will explain how new command types are added without changing the main API or worker flow.

Post-design re-check: PASS. Research, data model, contracts, and quickstart preserve the existing architecture and define documentation validation without changing domain/infrastructure boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/002-swagger-code-docs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── documentation-contract.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
app/
├── domain/
│   ├── command.py       # Add concise docstrings for entity and lifecycle invariants
│   ├── context.py       # Add concise docstrings for shared handler context
│   ├── handlers.py      # Add concise docstrings for base handler responsibilities
│   ├── ports.py         # Add concise docstrings for ports/contracts
│   └── status.py        # Add concise docstrings for command lifecycle states
├── application/
│   ├── submit_command.py
│   ├── process_command.py
│   ├── handler_registry.py
│   └── pipelines.py
├── infrastructure/
│   ├── redis_queue.py
│   ├── redis_command_repository.py
│   ├── memory_command_repository.py
│   └── logging.py
├── api/
│   ├── main.py          # Configure API metadata/docs visibility
│   ├── schemas.py       # Add schema descriptions/examples
│   └── routes.py        # Add operation summary/description/responses/examples
├── worker/
│   └── main.py
└── commands/
    └── test_command/
        ├── pipeline.py
        └── handlers.py

tests/
├── test_api.py
├── test_documentation.py
└── test_architecture.py

README.md
```

**Structure Decision**: Update existing modules in place. Do not introduce a separate docs service or documentation generator because the current web framework already exposes interactive API documentation and schema generation.

## Complexity Tracking

No constitution violations or unjustified complexity are planned.
