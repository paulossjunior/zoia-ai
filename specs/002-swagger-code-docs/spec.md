# Feature Specification: Swagger and Code Documentation

**Feature Branch**: `002-swagger-code-docs`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "adicione swagger e documente o codigo"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore Command API Documentation (Priority: P1)

As an external integrator, I want an interactive API documentation page so that I can understand how to submit commands and inspect request, response, and error formats without reading source code.

**Why this priority**: The command submission endpoint is the main integration surface, and external systems need a reliable, discoverable contract.

**Independent Test**: Can be tested by opening the API documentation page, locating `POST /commands`, and confirming the documented request body, success response, and validation error response match the command submission contract.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** an integrator opens the interactive API documentation page, **Then** the page is reachable and lists `POST /commands`.
2. **Given** the documentation page is open, **When** the integrator expands `POST /commands`, **Then** the required `type` and `payload` request fields are visible.
3. **Given** the integrator reviews the endpoint responses, **When** they inspect success and validation responses, **Then** `202` and `400` outcomes are documented with example bodies.

---

### User Story 2 - Understand Command Processing Code (Priority: P2)

As a developer maintaining the service, I want concise documentation in the important code paths so that I can understand command submission, queueing, worker processing, and handler extension points safely.

**Why this priority**: The project uses layered architecture and asynchronous processing; maintainers need clear guidance at boundaries where misuse could violate the constitution.

**Independent Test**: Can be tested by reviewing the domain, application, infrastructure, API, worker, and command pipeline modules and confirming public classes/functions and extension points have concise documentation.

**Acceptance Scenarios**:

1. **Given** a developer opens the command processing modules, **When** they inspect public classes and functions, **Then** each important boundary has a concise explanation of its responsibility.
2. **Given** a developer wants to add a new command type, **When** they read the handler registry and command pipeline documentation, **Then** they can identify where to create and register a new pipeline without changing the worker flow.
3. **Given** a developer reviews domain modules, **When** they read documentation, **Then** the text reinforces that domain code remains free of infrastructure dependencies.

---

### User Story 3 - Use Documentation During Local Validation (Priority: P3)

As a developer or tester, I want the README to reference the API documentation page and code documentation expectations so that local validation includes documentation quality, not only runtime behavior.

**Why this priority**: Runtime documentation is most useful when developers know how to access and verify it during normal local workflows.

**Independent Test**: Can be tested by following the README instructions to start the service, open the API docs, submit a documented example command, and verify the code documentation guidance is present.

**Acceptance Scenarios**:

1. **Given** a developer follows the README, **When** the service starts locally, **Then** the README tells them where to open the API documentation page.
2. **Given** the developer reads the README, **When** they look for documentation expectations, **Then** the README explains which code areas must remain documented for future command types.

### Edge Cases

- The API documentation page is unavailable while the service is running: this must be treated as a documentation regression.
- The documented request or response schema differs from actual endpoint validation: the documentation must be corrected before release.
- Documentation exposes internal infrastructure details as public API behavior: the wording must be revised to keep integration docs focused on external contracts.
- Code documentation becomes verbose enough to obscure behavior: comments should be concise and focused on responsibilities, invariants, or extension points.
- A new command type is added later without documenting its payload contract: review must require documentation before acceptance.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose an interactive API documentation page for external integrators.
- **FR-002**: The API documentation MUST include the `POST /commands` operation.
- **FR-003**: The `POST /commands` documentation MUST show required request fields `type` and `payload`.
- **FR-004**: The `POST /commands` documentation MUST show the successful acknowledgement response containing `command_id` and `status`.
- **FR-005**: The API documentation MUST describe validation error responses for invalid command submissions.
- **FR-006**: The API documentation MUST include at least one valid command submission example.
- **FR-007**: Public code modules that define command lifecycle, queueing, processing, handler registry, API boundary, worker loop, and command pipeline behavior MUST include concise documentation of responsibility and key invariants.
- **FR-008**: Documentation for handler extensibility MUST explain how a new command type is added without changing the main API or worker flow.
- **FR-009**: Documentation MUST reinforce that domain code does not depend on infrastructure or web framework concerns.
- **FR-010**: README instructions MUST tell developers how to access the API documentation page in the local environment.
- **FR-011**: README instructions MUST include a documented example request that matches the interactive API documentation.
- **FR-012**: Documentation MUST avoid exposing queue implementation details as requirements for external clients.

### Key Entities

- **API Documentation Page**: Interactive documentation surface used by external integrators to inspect command submission contracts.
- **Command API Contract**: The documented request, response, and error shapes for command submission.
- **Code Documentation**: Concise module, class, and function explanations that describe responsibilities, invariants, and extension points.
- **Extension Guidance**: Documentation that explains how to add new command handlers/pipelines without changing the main flow.

### Contracts *(include if feature exposes inputs or outputs)*

- **Command Submission Documentation Contract**: Must document `POST /commands`, request fields, `202` acknowledgement, `400` validation errors, and example payloads.
- **Developer Documentation Contract**: Must document key source modules and README instructions needed to maintain and extend command processing safely.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can open the local API documentation page within 1 minute of starting the service.
- **SC-002**: 100% of documented `POST /commands` request and response examples match the actual endpoint behavior.
- **SC-003**: 100% of public command-processing modules include concise documentation for responsibilities or extension points.
- **SC-004**: A developer can identify the steps to add a new command type from documentation in under 5 minutes.
- **SC-005**: Documentation validation confirms no public API docs require external clients to know the queue implementation.

## Assumptions

- The existing command processing feature remains the primary API surface to document.
- The local service already has a discoverable interactive documentation mechanism available through the web application framework.
- Documentation should be concise and maintainable rather than exhaustive line-by-line comments.
- Generated interactive API documentation and README content should remain aligned with the actual request/response models.
