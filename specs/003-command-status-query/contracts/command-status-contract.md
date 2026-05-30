# Contract: Command Status Query

## Operation

```text
GET /commands/{command_id}
```

Returns the current lifecycle state for a previously submitted command.

## Path Parameters

| Name | Required | Description |
|------|----------|-------------|
| `command_id` | Yes | UUID command identifier returned by `POST /commands` |

## Success Response

Status: `200 OK`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "TEST_COMMAND",
  "status": "completed",
  "created_at": "2026-05-30T19:00:00Z",
  "started_at": "2026-05-30T19:00:01Z",
  "completed_at": "2026-05-30T19:00:02Z",
  "error_message": null
}
```

## Status Values

- `queued`
- `processing`
- `completed`
- `failed`

## Error Responses

Malformed identifier:

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

## Contract Rules

- The response never includes the original command payload.
- The operation is read-only and does not enqueue or process commands.
- Clients only need the command identifier returned by submission.
- Queue and storage implementation details are not part of the public contract.
- The operation must be documented in the interactive API documentation with success and error examples.
