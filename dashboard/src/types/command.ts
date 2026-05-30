export const commandStatuses = ['queued', 'processing', 'completed', 'failed'] as const
export const callbackStatuses = ['not_required', 'pending', 'sent', 'failed'] as const
export const sortFields = [
  'request_received_at',
  'processing_started_at',
  'processing_finished_at',
  'status',
  'type'
] as const

export type CommandStatus = (typeof commandStatuses)[number]
export type CallbackStatus = (typeof callbackStatuses)[number]
export type SortField = (typeof sortFields)[number]
export type SortDirection = 'asc' | 'desc'
export type JsonValue = unknown

export interface DashboardIndicators {
  total_commands: number
  queued_commands: number
  processing_commands: number
  completed_commands: number
  failed_commands: number
  callback_not_required: number
  callback_pending: number
  callback_sent: number
  callback_failed: number
}

export interface CommandListItem {
  command_id: string
  type: string
  external_id: string | null
  status: CommandStatus
  callback_status: CallbackStatus
  request_received_at: string
  processing_started_at?: string | null
  processing_finished_at: string | null
}

export interface CommandDetail extends CommandListItem {
  processing_started_at: string | null
  callback: string | null
  callback_error_message: string | null
  callback_sent_at: string | null
  payload: JsonValue
  response_payload: JsonValue
  error_message: string | null
}

export interface DashboardFilters {
  status: CommandStatus | ''
  type: string
  external_id: string
  callback_status: CallbackStatus | ''
  received_from: string
  received_to: string
  processing_from: string
  processing_to: string
  search: string
}

export interface Pagination {
  page: number
  page_size: number
  total: number
}

export interface Sorting {
  sort_by: SortField
  sort_direction: SortDirection
}

export interface CommandListResponse {
  items: CommandListItem[]
  total: number
  page: number
  page_size: number
}

export const defaultFilters = (): DashboardFilters => ({
  status: '',
  type: '',
  external_id: '',
  callback_status: '',
  received_from: '',
  received_to: '',
  processing_from: '',
  processing_to: '',
  search: ''
})

export const defaultPagination = (): Pagination => ({
  page: 1,
  page_size: 20,
  total: 0
})

export const defaultSorting = (): Sorting => ({
  sort_by: 'request_received_at',
  sort_direction: 'desc'
})

export const emptyIndicators = (): DashboardIndicators => ({
  total_commands: 0,
  queued_commands: 0,
  processing_commands: 0,
  completed_commands: 0,
  failed_commands: 0,
  callback_not_required: 0,
  callback_pending: 0,
  callback_sent: 0,
  callback_failed: 0
})
