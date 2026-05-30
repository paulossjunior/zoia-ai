<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- placeholder PRINCIPLE_1_NAME -> I. Domain-Oriented Architecture
- placeholder PRINCIPLE_2_NAME -> II. Asynchronous Command Processing
- placeholder PRINCIPLE_3_NAME -> III. Explicit Contracts
- placeholder PRINCIPLE_4_NAME -> IV. Low Infrastructure Coupling
- placeholder PRINCIPLE_5_NAME -> V. Mandatory Observability
Added principles:
- VI. Tests Before or With Implementation
- VII. Handler-Based Extensibility
Added sections:
- Architecture and Contract Standards
- Development Workflow and Quality Gates
Removed sections:
- Placeholder SECTION_2_NAME
- Placeholder SECTION_3_NAME
Templates requiring updates:
- UPDATED .specify/templates/plan-template.md
- UPDATED .specify/templates/spec-template.md
- UPDATED .specify/templates/tasks-template.md
- UPDATED .specify/templates/checklist-template.md
- NOT PRESENT .specify/templates/commands/*.md
- UPDATED AGENTS.md
Follow-up TODOs:
- None
-->
# Zoia AI Constitution

## Core Principles

### I. Domain-Oriented Architecture

The system MUST separate domain, application, and infrastructure concerns.
Domain code MUST NOT depend on Redis, databases, web frameworks, queue products,
or external libraries. Use cases MUST live in the application layer. External
technologies MUST live in the infrastructure layer.

Rationale: business rules remain understandable, testable, and portable when
they are not coupled to delivery or persistence mechanisms.

### II. Asynchronous Command Processing

Heavy or long-running work MUST execute asynchronously through commands. The
HTTP API MUST only validate, record, and enqueue commands. Real processing MUST
occur in independent workers. Every command MUST contain `type`, `payload`,
`status`, and `command_id`. Every `type` MUST be handled by a specific handler.

Rationale: request handling stays fast and reliable while workers own execution,
retries, and failure reporting.

### III. Explicit Contracts

Every system input and output MUST have a clear contract. APIs MUST document
requests, responses, and error shapes. Payloads MUST be validated before
enqueueing. Missing required fields MUST return HTTP 400. Allowed states MUST be
explicit and finite.

Rationale: explicit contracts make integrations predictable and prevent invalid
work from entering asynchronous flows.

### IV. Low Infrastructure Coupling

Infrastructure MUST be replaceable. Redis, queues, databases, and external
services MUST be accessed through interfaces. Domain code MUST NOT import
infrastructure code. Adapters MUST implement ports or interfaces defined by the
application layer.

Rationale: infrastructure choices can change without rewriting business logic or
application use cases.

### V. Mandatory Observability

Asynchronous flows MUST be traceable. Every command MUST record status changes.
Submission, processing start, success, and failure MUST produce logs. Processing
errors MUST include clear messages. Worker errors MUST NOT be silent.

Rationale: asynchronous execution removes the client from the final result path,
so operators need reliable status and logs to diagnose outcomes.

### VI. Tests Before or With Implementation

Every feature MUST include tests before or alongside implementation. Tests MUST
cover success paths, validation errors, handler failures, queue integration via
adapter or mock, and proof that the API does not execute command processing
directly.

Rationale: command workflows cross boundaries and fail in different phases;
tests protect the contract and the asynchronous behavior.

### VII. Handler-Based Extensibility

New command types MUST be added without changing the main submission or worker
flow. Workers MUST use a handler registry. Each handler MUST declare the command
`types` it supports. A new command MUST require only a new handler and a payload
contract.

Rationale: command processing remains open to new business capabilities while
the core orchestration stays stable.

## Architecture and Contract Standards

Feature plans MUST identify domain, application, and infrastructure boundaries
before implementation. Any direct dependency from domain to infrastructure is a
constitution violation unless the constitution is amended first.

Command-oriented features MUST define the command contract, payload validation,
status lifecycle, handler resolution behavior, and failure behavior. Queue
products and persistence products are implementation details and MUST be hidden
behind application-defined interfaces.

API-facing features MUST document request bodies, response bodies, error
responses, required fields, and all explicit state values. Invalid input MUST be
rejected before side effects that create asynchronous work.

## Development Workflow and Quality Gates

Plans MUST pass a Constitution Check before research and again after design.
The check MUST verify layered architecture, infrastructure abstraction, explicit
contracts, observability, handler extensibility, and required tests.

Task lists MUST include tests for each feature story and MUST include
observability tasks for asynchronous flows. Implementations MUST prove that HTTP
submission does not execute worker handler logic directly.

Reviews MUST reject changes that introduce direct infrastructure dependencies in
domain code, hidden worker errors, undocumented contracts, or new command types
that bypass the handler registry.

## Governance

This constitution supersedes conflicting project practices, templates, and
informal conventions. Amendments MUST update this file, include a Sync Impact
Report, and propagate required changes to affected templates and guidance files.

Versioning follows semantic versioning:
- MAJOR for incompatible principle removals or redefinitions.
- MINOR for new principles or materially expanded governance.
- PATCH for clarifications, wording changes, and non-semantic refinements.

Every plan, task list, and review MUST verify compliance with the active
constitution. Exceptions MUST be documented in the plan's Complexity Tracking
section with the reason and the simpler alternative that was rejected.

**Version**: 1.0.0 | **Ratified**: 2026-05-30 | **Last Amended**: 2026-05-30
