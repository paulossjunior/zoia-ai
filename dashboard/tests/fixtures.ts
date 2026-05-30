import type {
  CommandDetail,
  CommandListItem,
  CommandListResponse,
  DashboardIndicators
} from '@/types/command'

export const indicatorsFixture: DashboardIndicators = {
  total_commands: 4,
  queued_commands: 1,
  processing_commands: 1,
  completed_commands: 1,
  failed_commands: 1,
  callback_not_required: 1,
  callback_pending: 1,
  callback_sent: 1,
  callback_failed: 1
}

export const emptyIndicatorsFixture: DashboardIndicators = {
  total_commands: 0,
  queued_commands: 0,
  processing_commands: 0,
  completed_commands: 0,
  failed_commands: 0,
  callback_not_required: 0,
  callback_pending: 0,
  callback_sent: 0,
  callback_failed: 0
}

export const commandListFixture: CommandListItem[] = [
  {
    command_id: '00000000-0000-4000-8000-000000000001',
    type: 'TEST_COMMAND',
    external_id: 'BOLSISTA-123',
    status: 'completed',
    callback_status: 'sent',
    request_received_at: '2026-05-30T10:00:00Z',
    processing_started_at: '2026-05-30T10:00:01Z',
    processing_finished_at: '2026-05-30T10:00:03Z'
  },
  {
    command_id: '00000000-0000-4000-8000-000000000002',
    type: 'SEND_EMAIL',
    external_id: null,
    status: 'failed',
    callback_status: 'failed',
    request_received_at: '2026-05-30T11:00:00Z',
    processing_started_at: '2026-05-30T11:00:01Z',
    processing_finished_at: '2026-05-30T11:00:02Z'
  }
]

export const commandListResponseFixture: CommandListResponse = {
  items: commandListFixture,
  total: commandListFixture.length,
  page: 1,
  page_size: 20
}

export const commandDetailFixture: CommandDetail = {
  ...commandListFixture[0],
  processing_started_at: commandListFixture[0].processing_started_at ?? null,
  callback: 'https://sistema-origem.com/api/callback',
  callback_error_message: null,
  callback_sent_at: '2026-05-30T10:00:04Z',
  payload: {
    message: 'hello',
    nested: { active: true }
  },
  response_payload: {
    echo: 'hello'
  },
  error_message: null
}

export const failingCommandDetailFixture: CommandDetail = {
  ...commandListFixture[1],
  processing_started_at: commandListFixture[1].processing_started_at ?? null,
  callback: 'https://sistema-origem.com/api/callback',
  callback_error_message: 'timeout',
  callback_sent_at: null,
  payload: { to: 'aluno@ifes.edu.br' },
  response_payload: null,
  error_message: 'handler failed'
}
