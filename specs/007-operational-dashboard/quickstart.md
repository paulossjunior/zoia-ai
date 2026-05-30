# Quickstart: Operational Command Dashboard

## Prerequisites

- Command API and worker environment running locally.
- Persisted command records available for dashboard display.
- Dashboard frontend configured with the backend base URL.

## Local Development

```bash
cd dashboard
npm install
npm run dev
```

Open the dashboard in a browser:

```text
http://localhost:5173/dashboard
```

## Docker Compose

Start the full local environment:

```bash
docker compose up --build
```

Expected services:

- API service
- worker service
- Redis
- PostgreSQL
- RedisInsight
- dashboard frontend

Open:

```text
http://localhost:5173/dashboard
```

The dashboard service is read-only and talks to the API service through:

```text
GET /dashboard/indicators
GET /dashboard/commands
GET /dashboard/commands/{command_id}
```

## Validate Indicators

1. Submit or seed commands in different statuses.
2. Open the dashboard.
3. Confirm indicator cards show:
   - Total commands
   - queued
   - processing
   - completed
   - failed
   - callback not_required
   - callback pending
   - callback sent
   - callback failed

## Validate Command List

1. Open the dashboard.
2. Confirm the table shows Command ID, Type, External ID, Status, Callback Status, receipt date, finish date, and actions.
3. Change page and page size.
4. Sort by receipt date, processing start date, processing finish date, status, and type.

## Validate Filters and Search

Apply filters for:

- Status
- Type
- External ID
- Callback Status
- Receipt period
- Processing period

Search for:

- A known Command ID
- A known External ID

The command list should reload using the selected criteria.

## Validate Details

1. Click "Visualizar detalhes" for a command row.
2. Confirm the drawer or modal shows:
   - Command identification
   - Processing dates
   - Callback data
   - Original payload as formatted JSON
   - Response payload as formatted JSON
   - Error message when present

## Validate UI States

- Stop or misconfigure the backend and confirm the dashboard shows "Não foi possível carregar os dados."
- Use an empty command dataset and confirm the dashboard shows "O sistema não possui comandos registrados."
- Trigger manual refresh and confirm filters and pagination are preserved.

## Run Tests

```bash
cd dashboard
npm test
npm run build
```

Expected coverage:

- Indicators loading and rendering
- Command table loading
- Pagination
- Sorting
- Filters
- Search by command id and external id
- Details drawer/modal
- JSON viewer
- Loading, empty, and error states
- Manual refresh behavior
