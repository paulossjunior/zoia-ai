# Research: Operational Command Dashboard

## Decision: Build the dashboard as a separate frontend application

**Rationale**: The current service is a Python command API and worker. The dashboard is a browser interface with its own routing, state, components, and tests. A dedicated `dashboard/` app keeps frontend concerns separate from backend command processing and makes the read-only boundary clear.

**Alternatives considered**: Embedding dashboard assets directly into the backend was rejected because it would mix UI build tooling with the service boundary. Building the dashboard inside `app/` was rejected because that path is already organized around backend domain, application, infrastructure, API, and worker layers.

## Decision: Use Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind CSS, and Axios

**Rationale**: The copied technical brief explicitly selects this stack. Vue 3 and TypeScript provide typed component development, Vite gives a lightweight local dev/build setup, Pinia centralizes dashboard state, Vue Router provides a stable dashboard route, Tailwind CSS supports responsive operational UI without large custom CSS, and Axios encapsulates backend calls through a service layer.

**Alternatives considered**: Plain HTML/JavaScript was rejected because the dashboard needs typed contracts, state, tests, and reusable components. A backend-rendered page was rejected because the feature calls for a modern frontend with client-side refresh, filtering, drawer/modal detail interaction, and component tests.

## Decision: Consume only backend read endpoints through a service layer

**Rationale**: The dashboard must not access PostgreSQL directly, consume queues, create commands, mutate status, or resend callbacks. A `dashboardService.ts` layer makes the backend integration explicit and testable while keeping components and store code free of raw HTTP details.

**Alternatives considered**: Direct component-level HTTP calls were rejected because they scatter integration behavior and make tests harder to control. Direct database access was rejected by the feature scope and project constitution.

## Decision: Keep all filters, sorting, pagination, and search in request parameters

**Rationale**: The copied technical brief says filters, pagination, ordering, and search must be sent to the backend through query parameters. This keeps the frontend read-only and avoids downloading all persisted records for client-side querying.

**Alternatives considered**: Client-side filtering of all records was rejected because it does not scale and would bypass backend query contracts. Creating custom frontend queries outside documented endpoints was rejected because the dashboard must use existing service endpoints.

## Decision: Model dashboard state in Pinia

**Rationale**: Indicators, command rows, filters, pagination, selected command, loading flags, and errors are shared across the dashboard view and components. A Pinia store gives one predictable state owner and supports unit tests for refresh, filter changes, detail loading, and error states.

**Alternatives considered**: Component-local state only was rejected because the dashboard has multiple coordinated controls and views. A heavier global state solution was rejected because this is a single dashboard feature.

## Decision: Use component-level tests with Vitest and Vue Testing Library

**Rationale**: The feature is primarily UI behavior. Tests should validate user-visible behavior: cards render, filters update requests, table pagination/sorting works, details open, JSON renders, and loading/empty/error states appear.

**Alternatives considered**: Only snapshot tests were rejected because they do not prove behavior. Only backend tests were rejected because the dashboard logic lives in the frontend.

## Decision: Prepare authentication integration without requiring it in v1

**Rationale**: The copied brief says to reuse authentication tokens and restrict access to ADMIN, OPERATOR, and VIEWER if authentication already exists. The current feature specification treats authentication as out of scope, so the plan should prepare the service layer for token injection while not blocking delivery on a missing auth feature.

**Alternatives considered**: Implementing a new authentication system was rejected as outside scope. Ignoring future auth entirely was rejected because the dashboard is operational and likely to require access control later.
