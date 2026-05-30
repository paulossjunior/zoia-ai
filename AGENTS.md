<!-- SPECKIT START -->
For this feature, read `specs/006-command-callback-persistence/plan.md` for the
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
