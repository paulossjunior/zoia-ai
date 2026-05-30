# Contract: Callback Delivery

Callback delivery occurs only when the original command included a non-blank `callback` URL.

## HTTP Request

```text
POST {callback}
```

## Success Payload

```json
{
  "external_id": "BOLSISTA-12345",
  "status": "completed",
  "payload": {
    "id": 123,
    "situacao": "importado"
  }
}
```

When `external_id` was not provided, omit it:

```json
{
  "status": "completed",
  "payload": {
    "id": 123,
    "situacao": "importado"
  }
}
```

## Failure Payload

```json
{
  "external_id": "BOLSISTA-12345",
  "status": "failed",
  "payload": {
    "message": "CPF ja cadastrado"
  }
}
```

When `external_id` was not provided, omit it:

```json
{
  "status": "failed",
  "payload": {
    "message": "CPF ja cadastrado"
  }
}
```

## Delivery Rules

- Callback is attempted only after processing reaches `completed` or `failed`.
- Callback is attempted for both success and failure outcomes when configured.
- Callback success sets `callback_status` to `sent` and records `callback_sent_at`.
- Callback failure sets `callback_status` to `failed` and records `callback_error_message`.
- Callback failure does not change command processing `status`.
- Callback failure does not remove `response_payload` or `error_message`.
- No HTTP request is attempted when callback is missing, null, or blank.
