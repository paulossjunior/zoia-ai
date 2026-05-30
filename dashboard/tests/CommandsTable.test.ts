import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'

import CommandsTable from '@/components/dashboard/CommandsTable.vue'

import { commandListFixture } from './fixtures'

describe('CommandsTable', () => {
  it('renders columns, rows, sorting, pagination, and detail action', async () => {
    const user = userEvent.setup()
    const { emitted } = render(CommandsTable, {
      props: {
        commands: commandListFixture,
        pagination: { page: 1, page_size: 20, total: 40 },
        sorting: { sort_by: 'request_received_at', sort_direction: 'desc' },
        loading: false
      }
    })

    expect(screen.getByText('Command ID')).toBeInTheDocument()
    expect(screen.getByText('TEST_COMMAND')).toBeInTheDocument()
    expect(screen.getByText('BOLSISTA-123')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Type' }))
    await user.click(screen.getAllByRole('button', { name: 'Visualizar detalhes' })[0])
    await user.click(screen.getByRole('button', { name: 'Próxima' }))

    expect(emitted('sortChange')).toBeTruthy()
    expect((emitted('viewDetails')?.[0][0] as string)).toBe(commandListFixture[0].command_id)
    expect(emitted('pageChange')).toBeTruthy()
  })
})
