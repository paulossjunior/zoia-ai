# Implementation Plan: Operational Command Dashboard

**Branch**: `007-operational-dashboard` | **Date**: 2026-05-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-operational-dashboard/spec.md` and copied technical brief for a Vue-based read-only dashboard.

## Summary

Build a modern, responsive, read-only operational dashboard frontend for monitoring persisted command processing data. The dashboard will be a Vue 3 + TypeScript application built with Vite, Pinia, Vue Router, Tailwind CSS, and Axios. It will consume only backend-provided read endpoints, display operational indicators, support filtered/sorted/paginated command browsing, show full command details in a drawer/modal, render payload and response JSON readably, and provide loading, empty, error, and manual refresh states. The dashboard will not create commands, process queues, access PostgreSQL directly, alter status, or resend callbacks.

## Technical Context

**Language/Version**: TypeScript with Vue 3; existing backend remains Python 3.12  
**Primary Dependencies**: Vue 3, Vite, Pinia, Vue Router, Tailwind CSS, Axios; existing backend command service endpoints  
**Storage**: No frontend persistence beyond in-memory UI/store state; persisted command data remains owned by the backend service  
**Testing**: Vitest and Vue Testing Library for frontend unit/component tests; existing pytest suite for backend regression checks if contracts are added or adjusted  
**Target Platform**: Browser-based web dashboard served locally through Docker Compose and usable on desktop, tablet, and mobile viewports  
**Project Type**: Frontend web application integrated with an existing backend service  
**Performance Goals**: Dashboard initial view should show loading feedback immediately; indicator and list refresh should complete within normal operator expectations for paginated data; table interactions should avoid full-page reloads  
**Constraints**: Dashboard is strictly read-only; no direct PostgreSQL access; no queue consumption; no command creation; no status mutation; no callback execution; filters, pagination, sorting, and search are sent through backend query parameters  
**Scale/Scope**: One dashboard route/view, reusable dashboard components, service layer, Pinia store, typed command contracts, Docker Compose service, and tests for indicators, list, filters, search, details, JSON viewer, and UI states

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Domain boundaries**: PASS. The feature is a frontend read-only monitoring surface. It must not change backend domain logic. Any optional backend contract support must remain in application/infrastructure layers and keep `app/domain/` free of frontend, database, queue, or HTTP framework dependencies.
- **Asynchronous command flow**: PASS. The dashboard does not submit or process commands. It only observes already persisted command state and must not enqueue, consume queues, or execute worker handlers.
- **Explicit contracts**: PASS. The feature requires typed contracts for dashboard indicators, command list query/response, command detail response, loading/error/empty states, allowed sort fields, allowed command statuses, and allowed callback statuses.
- **Infrastructure abstraction**: PASS. The frontend talks only to backend read endpoints through `dashboardService.ts`. It does not access PostgreSQL or Redis directly. Backend persistence/queue adapters remain hidden behind existing backend boundaries.
- **Observability**: PASS. No command status transitions are introduced. The dashboard should preserve existing backend observability and may surface load errors to users; no worker errors may be hidden or modified by the frontend.
- **Testing discipline**: PASS. Tests must cover indicator loading, command list loading, pagination, sorting, filtering, search, details drawer/modal, JSON rendering, loading state, empty state, error state, manual refresh, and proof that service calls are read-only.
- **Handler extensibility**: PASS. The dashboard displays command `type` values generically and does not require worker or handler flow changes for new command types.

Post-design re-check: PASS. The design artifacts keep the dashboard frontend isolated from command processing, preserve backend domain boundaries, document typed read contracts, and require tests for read-only behavior and major UI states.

## Project Structure

### Documentation (this feature)

```text
specs/007-operational-dashboard/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── dashboard-api-contract.md
│   └── dashboard-ui-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
dashboard/
├── Dockerfile
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── views/
│   │   └── DashboardView.vue
│   ├── components/
│   │   └── dashboard/
│   │       ├── DashboardHeader.vue
│   │       ├── IndicatorsGrid.vue
│   │       ├── IndicatorCard.vue
│   │       ├── CommandsTable.vue
│   │       ├── CommandsFilters.vue
│   │       ├── CommandDetailsDrawer.vue
│   │       ├── JsonViewer.vue
│   │       ├── EmptyState.vue
│   │       ├── LoadingState.vue
│   │       ├── ErrorState.vue
│   │       └── RefreshButton.vue
│   ├── router/
│   │   └── index.ts
│   ├── services/
│   │   └── dashboardService.ts
│   ├── stores/
│   │   └── dashboardStore.ts
│   ├── types/
│   │   └── command.ts
│   └── test/
│       └── setup.ts
└── tests/
    ├── dashboardService.test.ts
    ├── dashboardStore.test.ts
    ├── DashboardView.test.ts
    ├── CommandsTable.test.ts
    ├── CommandsFilters.test.ts
    ├── CommandDetailsDrawer.test.ts
    ├── JsonViewer.test.ts
    └── states.test.ts

docker-compose.yml
README.md
docs/backlog.md
```

**Structure Decision**: Add a dedicated `dashboard/` frontend application at the repository root. This keeps the existing Python command service unchanged while allowing Docker Compose to run the dashboard as a separate service that consumes the backend read endpoints.

## Complexity Tracking

No constitution violations or additional complexity are planned.
