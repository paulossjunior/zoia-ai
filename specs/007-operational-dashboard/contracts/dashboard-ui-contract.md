# Contract: Dashboard UI Behavior

## Main View

Route:

```text
/dashboard
```

The main view contains:

- Dashboard header
- Manual refresh button
- Indicator cards
- Command filters
- Search control
- Command table
- Pagination controls
- Command details drawer or modal

## Indicator Cards

Required cards:

- Total de comandos
- Total em fila
- Total em processamento
- Total concluídos
- Total com falha
- Total callback not_required
- Total callback pending
- Total callback sent
- Total callback failed

Critical indicators such as failed commands and failed callbacks should be
visually distinguishable from neutral indicators.

## Command Table

Required columns:

- Command ID
- Type
- External ID
- Status
- Callback Status
- Recebido em
- Finalizado em
- Ações

Required action:

- Visualizar detalhes

Default ordering:

```text
request_received_at desc
```

## Filters

Filter controls must support:

- Status
- Type
- External ID
- Callback Status
- Data inicial de recebimento
- Data final de recebimento
- Data inicial de processamento
- Data final de processamento

Applying filters reloads the command list using the selected criteria.

## Search

Search supports:

- Command ID
- External ID

Search input is sent through the service layer to the backend. Command ID
matches are expected to locate a specific command. External ID searches may
return multiple commands.

## Details Drawer or Modal

Sections:

- Identification: Command ID, Type, External ID
- Processing: Status, Request Received At, Processing Started At, Processing Finished At
- Callback: Callback URL, Callback Status, Callback Error Message, Callback Sent At
- Payload: formatted original payload JSON
- Response: formatted response payload JSON
- Errors: Error Message

## JsonViewer

The JSON viewer must:

- Format JSON automatically
- Display hierarchical structure
- Allow expanding and collapsing nested objects and arrays
- Allow copying content
- Handle null values
- Handle empty objects
- Handle empty payloads

## UI States

### Loading

The dashboard displays skeletons, placeholders, or another visual loading
indicator while data is loading.

### Empty

When no records are available, display:

```text
O sistema não possui comandos registrados.
```

### Error

When data cannot be loaded, display:

```text
Não foi possível carregar os dados.
```

### Refresh

Manual refresh reloads indicators and the current command list while preserving
active filters, sorting, pagination, and search criteria.

## Responsive Behavior

The dashboard must work on:

- Desktop
- Tablet
- Mobile

The command table may adapt on smaller screens through horizontal scrolling,
compact rows, stacked metadata, or another readable layout.

## Read-Only Guarantees

The UI must not expose actions for:

- Creating commands
- Processing commands
- Consuming queues
- Changing command status
- Modifying persisted command data
- Resending callbacks
