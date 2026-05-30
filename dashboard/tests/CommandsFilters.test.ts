import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'

import CommandsFilters from '@/components/dashboard/CommandsFilters.vue'
import { defaultFilters } from '@/types/command'

describe('CommandsFilters', () => {
  it('emits combined filters', async () => {
    const user = userEvent.setup()
    const { emitted } = render(CommandsFilters, {
      props: {
        filters: defaultFilters(),
        loading: false
      }
    })

    await user.selectOptions(screen.getByLabelText('Status'), 'failed')
    await user.type(screen.getByLabelText('Type'), 'SEND_EMAIL')
    await user.type(screen.getByLabelText('External ID'), 'BOLSISTA-123')
    await user.type(screen.getByLabelText('Pesquisar Command ID ou External ID'), '0000')
    await user.click(screen.getByRole('button', { name: 'Aplicar' }))

    const appliedFilters = emitted('apply')?.[0][0] as Record<string, unknown>
    expect(appliedFilters).toMatchObject({
      status: 'failed',
      type: 'SEND_EMAIL',
      external_id: 'BOLSISTA-123',
      search: '0000'
    })
  })
})
