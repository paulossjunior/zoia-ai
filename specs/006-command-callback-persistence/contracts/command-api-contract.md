# Contract: Command API with Callback Persistence

## Submit Command

```text
POST /commands
```

### Full Request

```json
{
  "type": "IMPORT_BOLSISTA",
  "payload": {
    "nome": "Joao Silva",
    "cpf": "12345678900"
  },
  "external_id": "BOLSISTA-12345",
  "callback": "https://sistema-origem.com/api/callback"
}
```

### Minimal Request

```json
{
  "type": "IMPORT_BOLSISTA",
  "payload": {
    "nome": "Joao Silva",
    "cpf": "12345678900"
  }
}
```

### Success Response

Status: `202 Accepted`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "queued"
}
```

### Validation Error

Status: `400 Bad Request`

```json
{
  "detail": "invalid command request"
}
```

## Get Command by Command Id

```text
GET /commands/{command_id}
```

### Success Response

Status: `200 OK`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "type": "IMPORT_BOLSISTA",
  "external_id": "BOLSISTA-12345",
  "callback": "https://sistema-origem.com/api/callback",
  "status": "completed",
  "payload": {
    "nome": "Joao Silva",
    "cpf": "12345678900"
  },
  "response_payload": {
    "id": 123,
    "situacao": "importado"
  },
  "error_message": null,
  "callback_status": "sent",
  "callback_error_message": null,
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z",
  "callback_sent_at": "2026-05-30T10:00:04Z"
}
```

## Get Command Status

```text
GET /commands/{command_id}/status
```

### Success Response

Status: `200 OK`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "status": "processing",
  "callback_status": "pending"
}
```

## Get Most Recent Command by External Id

```text
GET /commands/external/{external_id}
```

### Success Response

Status: `200 OK`

```json
{
  "command_id": "00000000-0000-4000-8000-000000000000",
  "external_id": "BOLSISTA-12345",
  "type": "IMPORT_BOLSISTA",
  "status": "completed",
  "payload": {
    "nome": "Joao Silva"
  },
  "response_payload": {
    "id": 123,
    "situacao": "importado"
  },
  "error_message": null,
  "callback_status": "sent",
  "callback_error_message": null,
  "request_received_at": "2026-05-30T10:00:00Z",
  "processing_started_at": "2026-05-30T10:00:01Z",
  "processing_finished_at": "2026-05-30T10:00:03Z",
  "callback_sent_at": "2026-05-30T10:00:04Z"
}
```

## Lookup Errors

Invalid command id:

Status: `400 Bad Request`

```json
{
  "detail": "invalid command_id"
}
```

Unknown command id or external id:

Status: `404 Not Found`

```json
{
  "detail": "command not found"
}
```
