# Tasks: Operational Command Dashboard

**Input**: Design documents from `/specs/007-operational-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the project constitution. Frontend tests use Vitest and Vue Testing Library, with service mocks to prove the dashboard is read-only and consumes only persisted command data through backend read contracts.

**Organization**: Tasks are grouped by user story so each story can be implemented, tested, and delivered independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or does not depend on incomplete tasks
- **[Story]**: User story label for story-specific tasks only
- Every task includes exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the independent Vue dashboard application, local tooling, Docker entrypoint, and shared project wiring.

- [X] T001 Inspect existing backend routes and Docker services to confirm dashboard integration points in `app/api/routes.py` and `docker-compose.yml`
- [X] T002 Create the dashboard directory structure from the implementation plan in `dashboard/src/`, `dashboard/tests/`, and `dashboard/src/components/dashboard/`
- [X] T003 Create Vue/Vite package metadata and scripts in `dashboard/package.json`
- [X] T004 [P] Configure TypeScript compiler options in `dashboard/tsconfig.json`
- [X] T005 [P] Configure Vite entrypoints and API proxy environment support in `dashboard/vite.config.ts`
- [X] T006 [P] Configure Vitest and Vue Testing Library setup in `dashboard/vitest.config.ts`
- [X] T007 [P] Configure Tailwind CSS and content paths in `dashboard/tailwind.config.ts`
- [X] T008 [P] Configure PostCSS for Tailwind in `dashboard/postcss.config.js`
- [X] T009 Create the browser HTML shell in `dashboard/index.html`
- [X] T010 Create the Vue application bootstrap in `dashboard/src/main.ts`
- [X] T011 Create the root application shell in `dashboard/src/App.vue`
- [X] T012 [P] Create the dashboard route definition in `dashboard/src/router/index.ts`
- [X] T013 [P] Create the frontend test setup file in `dashboard/src/test/setup.ts`
- [X] T014 [P] Add dashboard build artifacts and dependencies to ignore rules in `.gitignore`
- [X] T015 [P] Add dashboard Docker ignore rules in `dashboard/.dockerignore`
- [X] T016 Create the dashboard Docker image definition in `dashboard/Dockerfile`
- [X] T017 Add the read-only dashboard frontend service and environment variables to `docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish typed contracts, service access, shared store, reusable UI states, and fixtures required by all dashboard stories.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T018 Define command status, callback status, indicator, list item, detail, filter, pagination, and sort TypeScript contracts in `dashboard/src/types/command.ts`
- [X] T019 [P] Create reusable test fixtures for dashboard metrics, command list items, command details, and API errors in `dashboard/tests/fixtures.ts`
- [X] T020 Create the Axios client factory and environment-driven API base URL in `dashboard/src/services/dashboardService.ts`
- [X] T021 Add read-only service methods for `GET /dashboard/indicators`, `GET /dashboard/commands`, and `GET /dashboard/commands/{command_id}` in `dashboard/src/services/dashboardService.ts`
- [X] T022 [P] Add service contract tests for endpoint paths, query serialization, and absence of POST/PUT/PATCH/DELETE calls in `dashboard/tests/dashboardService.test.ts`
- [X] T023 Create the Pinia dashboard store state for indicators, list, selected detail, filters, pagination, sorting, loading flags, and error messages in `dashboard/src/stores/dashboardStore.ts`
- [X] T024 Add store actions for loading indicators, loading command lists, loading details, setting filters, setting sorting, setting pagination, and clearing errors in `dashboard/src/stores/dashboardStore.ts`
- [X] T025 [P] Add foundational store tests for initial state and action state transitions in `dashboard/tests/dashboardStore.test.ts`
- [X] T026 [P] Create the loading state component with accessible loading text in `dashboard/src/components/dashboard/LoadingState.vue`
- [X] T027 [P] Create the empty state component with the message "O sistema não possui comandos registrados." in `dashboard/src/components/dashboard/EmptyState.vue`
- [X] T028 [P] Create the error state component with the message "Não foi possível carregar os dados." in `dashboard/src/components/dashboard/ErrorState.vue`
- [X] T029 [P] Create the reusable refresh button component skeleton in `dashboard/src/components/dashboard/RefreshButton.vue`
- [X] T030 [P] Create the dashboard header component skeleton in `dashboard/src/components/dashboard/DashboardHeader.vue`
- [X] T031 Create the main dashboard view skeleton with store initialization hooks in `dashboard/src/views/DashboardView.vue`
- [X] T032 [P] Add shared UI state component tests for loading, empty, and error messages in `dashboard/tests/states.test.ts`

**Checkpoint**: Dashboard foundation is ready; story work can proceed independently.

---

## Phase 3: User Story 1 - View Operational Indicators (Priority: P1) MVP

**Goal**: Operators can open the dashboard and see operational totals, command status distribution, callback status distribution, and loading/empty/error states without mutating command data.

**Independent Test**: Mock persisted command metrics in the dashboard service, load `/dashboard`, and verify all indicator values and distributions render while only read endpoints are called.

### Tests for User Story 1

- [X] T033 [P] [US1] Add component tests for indicator card labels, values, and status variants in `dashboard/tests/IndicatorsGrid.test.ts`
- [X] T034 [P] [US1] Add dashboard view tests for successful indicator loading and zero-record empty state in `dashboard/tests/DashboardView.test.ts`
- [X] T035 [P] [US1] Add dashboard view tests for indicator loading and loading-error states in `dashboard/tests/DashboardView.test.ts`
- [X] T036 [P] [US1] Add store tests for `loadIndicators` success, empty metrics, and failure handling in `dashboard/tests/dashboardStore.test.ts`

### Implementation for User Story 1

- [X] T037 [P] [US1] Implement metric display, semantic labels, and status styling in `dashboard/src/components/dashboard/IndicatorCard.vue`
- [X] T038 [US1] Implement total command, command status, and callback status sections in `dashboard/src/components/dashboard/IndicatorsGrid.vue`
- [X] T039 [US1] Wire indicator loading, loading state, empty state, and error state into `dashboard/src/views/DashboardView.vue`
- [X] T040 [US1] Add derived indicator getters for totals and zero-record detection in `dashboard/src/stores/dashboardStore.ts`
- [X] T041 [US1] Style the dashboard header and indicator layout for desktop, tablet, and mobile in `dashboard/src/components/dashboard/DashboardHeader.vue` and `dashboard/src/components/dashboard/IndicatorsGrid.vue`
- [X] T042 [US1] Add route-level mounting for the dashboard view at `/dashboard` in `dashboard/src/router/index.ts`

**Checkpoint**: User Story 1 is independently usable as the MVP dashboard view.

---

## Phase 4: User Story 2 - Browse and Filter Commands (Priority: P2)

**Goal**: Operators can browse, paginate, filter, sort, and search persisted command records in a read-only table.

**Independent Test**: Mock command records with varied statuses, types, external IDs, callback statuses, and timestamps, then verify filters, search, sorting, pagination, and default newest-first ordering through the dashboard UI.

### Tests for User Story 2

- [X] T043 [P] [US2] Add service tests for list query parameters including pagination, status, type, external ID, callback status, periods, search, and sorting in `dashboard/tests/dashboardService.test.ts`
- [X] T044 [P] [US2] Add store tests for filter merging, pagination updates, sorting updates, and list reload criteria in `dashboard/tests/dashboardStore.test.ts`
- [X] T045 [P] [US2] Add component tests for all filter controls and combined filter submission in `dashboard/tests/CommandsFilters.test.ts`
- [X] T046 [P] [US2] Add component tests for table columns, default newest-first rows, pagination controls, and sort controls in `dashboard/tests/CommandsTable.test.ts`
- [X] T047 [P] [US2] Add dashboard view tests for search by Command ID and External ID in `dashboard/tests/DashboardView.test.ts`
- [X] T048 [P] [US2] Add dashboard view tests for no-results empty state after filters or search in `dashboard/tests/DashboardView.test.ts`

### Implementation for User Story 2

- [X] T049 [US2] Implement typed list query serialization for filters, sorting, search, and pagination in `dashboard/src/services/dashboardService.ts`
- [X] T050 [US2] Implement filter state actions and list reload behavior in `dashboard/src/stores/dashboardStore.ts`
- [X] T051 [US2] Implement status, type, external ID, callback status, received period, processing period, and search inputs in `dashboard/src/components/dashboard/CommandsFilters.vue`
- [X] T052 [US2] Implement command table columns for Command ID, Type, External ID, Status, Callback Status, Data de Recebimento, and Data de Finalização in `dashboard/src/components/dashboard/CommandsTable.vue`
- [X] T053 [US2] Implement pagination controls and page-size handling in `dashboard/src/components/dashboard/CommandsTable.vue`
- [X] T054 [US2] Implement sortable headers for receipt date, processing start date, finish date, status, and type in `dashboard/src/components/dashboard/CommandsTable.vue`
- [X] T055 [US2] Wire filters, search, sorting, pagination, loading state, no-results state, and errors into `dashboard/src/views/DashboardView.vue`
- [X] T056 [US2] Add readable status and callback status badge styling in `dashboard/src/components/dashboard/CommandsTable.vue`
- [X] T057 [US2] Ensure the list defaults to `request_received_at` descending in `dashboard/src/stores/dashboardStore.ts`

**Checkpoint**: User Story 2 is independently usable for locating command records.

---

## Phase 5: User Story 3 - Inspect Command Details (Priority: P3)

**Goal**: Operators can select one command and inspect its full persisted audit record, including payload, response, errors, processing timestamps, and callback delivery data.

**Independent Test**: Mock a selected command detail and verify the details drawer shows every persisted section exactly, with formatted expandable JSON and no mutation calls.

### Tests for User Story 3

- [X] T058 [P] [US3] Add service tests for command detail loading and 404/error mapping in `dashboard/tests/dashboardService.test.ts`
- [X] T059 [P] [US3] Add store tests for selected command detail loading, detail errors, and clearing selected detail in `dashboard/tests/dashboardStore.test.ts`
- [X] T060 [P] [US3] Add JSON viewer tests for object, array, null, empty, nested, expand, and collapse behavior in `dashboard/tests/JsonViewer.test.ts`
- [X] T061 [P] [US3] Add details drawer tests for identification, processing, callback, payload, response, and error sections in `dashboard/tests/CommandDetailsDrawer.test.ts`
- [X] T062 [P] [US3] Add dashboard view tests for selecting a table row and opening details in `dashboard/tests/DashboardView.test.ts`

### Implementation for User Story 3

- [X] T063 [US3] Implement expandable and collapsible formatted JSON rendering in `dashboard/src/components/dashboard/JsonViewer.vue`
- [X] T064 [US3] Implement command detail loading action and selected-detail state in `dashboard/src/stores/dashboardStore.ts`
- [X] T065 [US3] Implement the details drawer layout with close behavior in `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`
- [X] T066 [US3] Add identification fields to the details drawer in `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`
- [X] T067 [US3] Add processing timestamp and status fields to the details drawer in `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`
- [X] T068 [US3] Add callback URL, callback status, callback error message, and callback sent date fields to the details drawer in `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`
- [X] T069 [US3] Add payload, response payload, and error message sections using `JsonViewer` in `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`
- [X] T070 [US3] Wire row selection from `CommandsTable` to detail loading and drawer display in `dashboard/src/views/DashboardView.vue`
- [X] T071 [US3] Add accessible focus management and keyboard close support to `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`

**Checkpoint**: User Story 3 is independently usable for command audit inspection.

---

## Phase 6: User Story 4 - Refresh Dashboard Data (Priority: P4)

**Goal**: Operators can manually refresh indicators and list data without a full page reload while preserving current filters, sorting, pagination, and visible data where possible.

**Independent Test**: Mock changed metrics and command list responses, click refresh, and verify indicators and list update using the current criteria with no page reload or mutation calls.

### Tests for User Story 4

- [X] T072 [P] [US4] Add refresh button component tests for click, disabled, and loading states in `dashboard/tests/RefreshButton.test.ts`
- [X] T073 [P] [US4] Add store tests for refresh preserving filters, sorting, pagination, and selected visible data on failure in `dashboard/tests/dashboardStore.test.ts`
- [X] T074 [P] [US4] Add dashboard view tests for manual refresh reloading indicators and command list without resetting criteria in `dashboard/tests/DashboardView.test.ts`

### Implementation for User Story 4

- [X] T075 [US4] Implement loading and disabled behavior in `dashboard/src/components/dashboard/RefreshButton.vue`
- [X] T076 [US4] Implement a store `refreshDashboard` action that reloads indicators and list with existing criteria in `dashboard/src/stores/dashboardStore.ts`
- [X] T077 [US4] Wire manual refresh into `DashboardHeader` and `DashboardView` in `dashboard/src/components/dashboard/DashboardHeader.vue` and `dashboard/src/views/DashboardView.vue`
- [X] T078 [US4] Preserve existing visible list and indicators when refresh fails in `dashboard/src/stores/dashboardStore.ts`
- [X] T079 [US4] Display refresh errors through the existing error state without forcing a full-page reload in `dashboard/src/views/DashboardView.vue`

**Checkpoint**: User Story 4 is independently usable for manual operational updates.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, runtime validation, responsive polish, and architectural guardrails across all stories.

- [X] T080 [P] Add responsive layout refinements and non-overlap checks for dashboard controls in `dashboard/src/views/DashboardView.vue`
- [X] T081 [P] Add keyboard and accessible label refinements in `dashboard/src/components/dashboard/CommandsFilters.vue`, `dashboard/src/components/dashboard/CommandsTable.vue`, `dashboard/src/components/dashboard/CommandDetailsDrawer.vue`, `dashboard/src/components/dashboard/JsonViewer.vue`, and `dashboard/src/components/dashboard/RefreshButton.vue`
- [X] T082 [P] Add a read-only architecture note for the dashboard feature in `docs/adr/0010-operational-dashboard-read-only-frontend.md`
- [X] T083 [P] Update the project backlog with dashboard epics, user stories, and tasks in `docs/backlog.md`
- [X] T084 Update README instructions for running the dashboard with Docker Compose in `README.md`
- [X] T085 Update quickstart validation notes for dashboard local execution in `specs/007-operational-dashboard/quickstart.md`
- [X] T086 Run frontend tests and fix any failures reported by `npm test` in `dashboard/package.json`
- [X] T087 Run frontend production build and fix any failures reported by `npm run build` in `dashboard/package.json`
- [X] T088 Run backend regression tests and fix dashboard-related regressions reported by `pytest` in `pyproject.toml`
- [X] T089 Run Docker Compose validation for `api`, `worker`, `redis`, `postgres`, `redisinsight`, and `dashboard` services in `docker-compose.yml`
- [X] T090 Verify the dashboard visually in a browser against the local Docker Compose stack and document the URL in `README.md`
- [X] T091 Validate that no dashboard code imports backend domain, Redis, PostgreSQL, queue, or worker modules in `dashboard/src/`
- [X] T092 Validate that generated tasks follow the strict checklist format in `specs/007-operational-dashboard/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; recommended MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can be developed after or alongside US1 if shared UI contracts are stable.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US2 table selection, but can be tested independently with direct detail mocks.
- **User Story 4 (Phase 6)**: Depends on Foundational and integrates with US1/US2 state, but can be tested independently with mocked store/service responses.
- **Polish (Phase 7)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 - View Operational Indicators**: No dependency on other stories after Foundational.
- **US2 - Browse and Filter Commands**: No dependency on US1 for service/store tests; UI composition shares DashboardView.
- **US3 - Inspect Command Details**: Uses command selection from US2 in the full UI, but detail service/store/drawer can be implemented and tested independently.
- **US4 - Refresh Dashboard Data**: Uses indicator and list state, but refresh behavior can be tested with mocked state and service responses.

### MVP Scope

Complete **Phase 1**, **Phase 2**, and **Phase 3 / US1** first. This delivers the initial operational dashboard with indicators, distributions, loading, empty, and error states.

---

## Parallel Execution Examples

### User Story 1

```bash
# Tests can be written in parallel:
Task: "T033 [P] [US1] Add component tests for indicator card labels, values, and status variants in dashboard/tests/IndicatorsGrid.test.ts"
Task: "T034 [P] [US1] Add dashboard view tests for successful indicator loading and zero-record empty state in dashboard/tests/DashboardView.test.ts"
Task: "T035 [P] [US1] Add dashboard view tests for indicator loading and loading-error states in dashboard/tests/DashboardView.test.ts"
Task: "T036 [P] [US1] Add store tests for loadIndicators success, empty metrics, and failure handling in dashboard/tests/dashboardStore.test.ts"
```

### User Story 2

```bash
# Tests can be written in parallel:
Task: "T043 [P] [US2] Add service tests for list query parameters including pagination, status, type, external ID, callback status, periods, search, and sorting in dashboard/tests/dashboardService.test.ts"
Task: "T045 [P] [US2] Add component tests for all filter controls and combined filter submission in dashboard/tests/CommandsFilters.test.ts"
Task: "T046 [P] [US2] Add component tests for table columns, default newest-first rows, pagination controls, and sort controls in dashboard/tests/CommandsTable.test.ts"
```

### User Story 3

```bash
# Tests can be written in parallel:
Task: "T058 [P] [US3] Add service tests for command detail loading and 404/error mapping in dashboard/tests/dashboardService.test.ts"
Task: "T060 [P] [US3] Add JSON viewer tests for object, array, null, empty, nested, expand, and collapse behavior in dashboard/tests/JsonViewer.test.ts"
Task: "T061 [P] [US3] Add details drawer tests for identification, processing, callback, payload, response, and error sections in dashboard/tests/CommandDetailsDrawer.test.ts"
```

### User Story 4

```bash
# Tests can be written in parallel:
Task: "T072 [P] [US4] Add refresh button component tests for click, disabled, and loading states in dashboard/tests/RefreshButton.test.ts"
Task: "T073 [P] [US4] Add store tests for refresh preserving filters, sorting, pagination, and selected visible data on failure in dashboard/tests/dashboardStore.test.ts"
Task: "T074 [P] [US4] Add dashboard view tests for manual refresh reloading indicators and command list without resetting criteria in dashboard/tests/DashboardView.test.ts"
```

---

## Implementation Strategy

### MVP First

1. Finish Setup and Foundational phases.
2. Implement US1 with tests until the dashboard shows operational indicators from read-only service mocks.
3. Validate `npm test` and `npm run build` inside `dashboard/`.

### Incremental Delivery

1. Add US2 list, filters, search, sort, and pagination.
2. Add US3 detail inspection and JSON viewer.
3. Add US4 manual refresh.
4. Complete Docker Compose, documentation, visual verification, and architecture checks.

### Read-Only Guardrail

Every service and UI task must preserve the dashboard as a query-only surface. The dashboard must not submit commands, consume queues, update statuses, write persisted records, or execute callbacks.
