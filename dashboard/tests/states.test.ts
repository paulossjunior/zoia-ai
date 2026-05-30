import { render, screen } from '@testing-library/vue'

import EmptyState from '@/components/dashboard/EmptyState.vue'
import ErrorState from '@/components/dashboard/ErrorState.vue'
import LoadingState from '@/components/dashboard/LoadingState.vue'

describe('dashboard states', () => {
  it('renders loading, empty, and error messages', () => {
    render(LoadingState)
    expect(screen.getByRole('status')).toHaveTextContent('Carregando dados...')

    render(EmptyState)
    expect(screen.getByText('O sistema não possui comandos registrados.')).toBeInTheDocument()

    render(ErrorState)
    expect(screen.getByRole('alert')).toHaveTextContent('Não foi possível carregar os dados.')
  })
})
