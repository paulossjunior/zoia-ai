<!-- SPECKIT START -->
For this feature, read `specs/007-operational-dashboard/plan.md` for the
current implementation plan, technologies, project structure, shell commands,
and other important information.
Also read `.specify/memory/constitution.md` before planning or implementing
features; its architecture, contract, observability, handler, and testing rules
are mandatory.
<!-- SPECKIT END -->

## Technical Documentation Skill

When creating or updating project documentation, use a technical documentation
workflow:

- Prefer concise, task-oriented docs that help a developer run, test, extend,
  or operate the service.
- Keep architecture decisions in `docs/adr/` using the ADR format: Status,
  Context, Decision, and Consequences.
- Keep README content focused on quickstart, local execution, API usage,
  worker behavior, observability, and extension points.
- Document public contracts with concrete request and response examples.
- Update docs together with code when behavior, APIs, environment variables,
  Docker services, or command lifecycle fields change.
- Validate documentation changes with `pytest tests/test_documentation.py`
  and `pytest tests/test_architecture.py` when applicable.

## Architecture Overview

Use this Mermaid diagram when explaining the current system architecture:

```mermaid
flowchart LR
    external["External System"] --> api["Command API"]
    operator["Operator/Admin"] --> dashboard["Operational Dashboard"]

    subgraph app_layers["Python Service"]
        api --> submit["SubmitCommand use case"]
        api --> queries["Read query use cases"]
        worker["Worker process"] --> process["ProcessCommand use case"]
        process --> registry["HandlerRegistry"]
        registry --> pipeline["Command Pipeline"]
        pipeline --> handlers["Command Handlers"]
    end

    submit --> store[("PostgreSQL Command Store")]
    submit --> queue[("Redis Command Queue")]
    worker --> queue
    process --> store
    queries --> store
    dashboard --> api

    api -. "no business processing" .-> submit
    dashboard -. "read only" .-> queries
```

Key boundaries:

- `app/domain` must not import FastAPI, Redis, PostgreSQL, Docker, HTTP clients,
  or dashboard code.
- API submission only validates, persists, enqueues, and returns `queued`.
- Worker processing is type-agnostic and resolves command behavior through the
  registry and pipeline.
- Dashboard is read-only and must not submit commands, process queues, mutate
  persisted records, or resend callbacks.
