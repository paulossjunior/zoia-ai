import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'

import RefreshButton from '@/components/dashboard/RefreshButton.vue'

describe('RefreshButton', () => {
  it('emits refresh and supports loading state', async () => {
    const user = userEvent.setup()
    const { emitted, rerender } = render(RefreshButton, { props: { loading: false } })

    await user.click(screen.getByRole('button', { name: 'Atualizar dashboard' }))
    expect(emitted('refresh')).toHaveLength(1)

    await rerender({ loading: true })
    expect(screen.getByRole('button', { name: 'Atualizar dashboard' })).toBeDisabled()
  })
})
