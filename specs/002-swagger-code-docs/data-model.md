# Data Model: Swagger and Code Documentation

## Entity: API Documentation Page

Represents the interactive documentation surface available while the service is running.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Local URL path for the documentation page |
| `operation_list` | list | Yes | Operations visible to integrators |
| `examples` | list | Yes | Example request/response bodies for command submission |

## Entity: Command API Documentation Contract

Represents the documented contract for submitting commands.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operation` | string | Yes | Must identify `POST /commands` |
| `request_schema` | object | Yes | Shows required `type` and `payload` fields |
| `success_response` | object | Yes | Shows `202` acknowledgement with `command_id` and `status` |
| `validation_response` | object | Yes | Shows `400` response for invalid submissions |
| `example_request` | object | Yes | At least one valid command submission example |

## Entity: Code Documentation

Represents concise documentation on public modules/classes/functions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | string | Yes | Module, class, or function being documented |
| `responsibility` | string | Yes | What the target owns |
| `invariants` | list | No | Boundary rules or lifecycle guarantees |
| `extension_guidance` | string | No | How maintainers should extend behavior safely |

## Validation Rules

- API docs must list `POST /commands`.
- API docs must show `type` and `payload` as required request fields.
- API docs must show `202` and `400` responses.
- Examples in README and API docs must match actual accepted payloads.
- Public command-processing modules must include concise docstrings at important boundaries.
- External-facing documentation must not require clients to know queue implementation details.
