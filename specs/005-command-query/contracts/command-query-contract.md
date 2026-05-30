# Contract: Command Query

## Get Command Details

```text
GET /commands/{id}
```

Returns the complete persisted command record.

### Success Response

Status: `200 OK`

```json
{
  "id": "5f5f97c5-66f0-43f5-bf57-55f36f7a2f9f",
  "type": "SEND_EMAIL",
  "status": "completed",
  "payload": {
    "to": "aluno@ifes.edu.br"
  },
  "response": {
    "message_id": "12345"
  },
  "error_message": null,
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z"
}
```

### Errors

Invalid identifier:

Status: `400 Bad Request`

```json
{
  "detail": "invalid command_id"
}
```

Unknown command:

Status: `404 Not Found`

```json
{
  "detail": "command not found"
}
```

## Get Command Status

```text
GET /commands/{id}/status
```

Returns only the current command status.

### Success Response

Status: `200 OK`

```json
{
  "id": "5f5f97c5-66f0-43f5-bf57-55f36f7a2f9f",
  "status": "processing"
}
```

### Errors

Uses the same invalid identifier and not-found error shapes as full detail lookup.

## List Commands

```text
GET /commands?status=failed&page=1&page_size=20
```

Lists command summaries, optionally filtered by status, with pagination metadata.

### Query Parameters

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `status` | No | none | Filter by `queued`, `processing`, `completed`, or `failed` |
| `page` | No | `1` | Page number, starting at 1 |
| `page_size` | No | `20` | Number of items per page |

### Success Response

Status: `200 OK`

```json
{
  "items": [
    {
      "id": "1",
      "type": "SEND_EMAIL",
      "status": "failed"
    },
    {
      "id": "2",
      "type": "GENERATE_REPORT",
      "status": "failed"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

### Errors

Invalid status filter:

Status: `400 Bad Request`

```json
{
  "detail": "invalid status"
}
```

Invalid pagination:

Status: `400 Bad Request`

```json
{
  "detail": "invalid pagination"
}
```

## Contract Rules

- Full detail lookup is read-only and must not enqueue or process work.
- Status-only lookup is read-only and must return only `id` and `status`.
- List responses must return summaries only.
- A status filter must restrict results to commands with the requested status.
- Unknown command ids must return 404.
- Storage technology details are not part of the public contract.
