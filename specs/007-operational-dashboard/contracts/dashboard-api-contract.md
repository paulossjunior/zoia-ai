# Contract: Dashboard Backend Read Endpoints

The dashboard consumes only read-only backend endpoints. The frontend must not
access persistence or queue infrastructure directly.

## Get Dashboard Indicators

```text
GET /dashboard/indicators
```

### Success Response

Status: `200 OK`

```json
{
  "total_commands": 120,
  "queued_commands": 8,
  "processing_commands": 3,
  "completed_commands": 100,
  "failed_commands": 9,
  "callback_not_required": 70,
  "callback_pending": 4,
  "callback_sent": 40,
  "callback_failed": 6
}
```

### Error Response

Status: `4xx` or `5xx`

The dashboard displays:

```text
Não foi possível carregar os dados.
```

## List Dashboard Commands

```text
GET /dashboard/commands
```

### Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page` | No | Page number starting at 1 |
| `page_size` | No | Number of rows per page |
| `status` | No | Command status filter |
| `type` | No | Command type filter |
| `external_id` | No | External id filter |
| `callback_status` | No | Callback status filter |
| `received_from` | No | Receipt period start |
| `received_to` | No | Receipt period end |
| `processing_from` | No | Processing period start |
| `processing_to` | No | Processing period end |
| `search` | No | Search text for command id or external id |
| `sort_by` | No | `request_received_at`, `processing_started_at`, `processing_finished_at`, `status`, or `type` |
| `sort_direction` | No | `asc` or `desc` |

### Success Response

Status: `200 OK`

```json
{
  "items": [
    {
      "command_id": "00000000-0000-4000-8000-000000000000",
      "type": "TEST_COMMAND",
      "external_id": "BOLSISTA-12345",
      "status": "completed",
      "callback_status": "sent",
      "request_received_at": "2026-05-30T10:00:00Z",
      "processing_finished_at": "2026-05-30T10:00:03Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Empty Response

Status: `200 OK`

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

The dashboard displays:

```text
O sistema não possui comandos registrados.
```

## Get Dashboard Command Detail

```text
GET /dashboard/commands/{command_id}
```

### Success Response

Status: `200 OK`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "external_id": "BOLSISTA-12345",
  "status": "completed",
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z",
  "callback": "https://sistema-origem.com/api/callback",
  "callback_status": "sent",
  "callback_error_message": null,
  "callback_sent_at": "2026-05-30T10:00:04Z",
  "payload": {
    "message": "hello"
  },
  "response_payload": {
    "echo": "hello"
  },
  "error_message": null
}
```

### Not Found Response

Status: `404 Not Found`

The dashboard displays:

```text
Não foi possível carregar os dados.
```

## Existing Command Detail Fallback

The dashboard may reuse existing read-only command endpoints when the dashboard
detail endpoint maps to the same contract:

```text
GET /commands/{command_id}
GET /commands/{command_id}/status
GET /commands/external/{external_id}
```

These endpoints remain read-only and must not be used for command mutation.
