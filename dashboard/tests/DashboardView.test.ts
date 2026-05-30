import { createPinia } from 'pinia'
import userEvent from '@testing-library/user-event'
import { render, screen, waitFor } from '@testing-library/vue'

import { setDashboardService, type DashboardService } from '@/services/dashboardService'
import DashboardView from '@/views/DashboardView.vue'

import {
  commandDetailFixture,
  commandListResponseFixture,
  emptyIndicatorsFixture,
  indicatorsFixture
} from './fixtures'

function serviceMock(overrides: Partial<DashboardService> = {}): DashboardService {
  return {
    getIndicators: vi.fn().mockResolvedValue(indicatorsFixture),
    listCommands: vi.fn().mockResolvedValue(commandListResponseFixture),
    getCommandDetail: vi.fn().mockResolvedValue(commandDetailFixture),
    ...overrides
  }
}

function renderDashboard(service: DashboardService = serviceMock()) {
  setDashboardService(service)
  return render(DashboardView, {
    global: {
      plugins: [createPinia()],
      stubs: {
        Teleport: true
      }
    }
  })
}

describe('DashboardView', () => {
  it('loads indicators and command list', async () => {
    renderDashboard()

    await waitFor(() => expect(screen.getByText('Total de comandos')).toBeInTheDocument())
    expect(await screen.findByText('TEST_COMMAND')).toBeInTheDocument()
    expect(screen.getByText('BOLSISTA-123')).toBeInTheDocument()
  })

  it('shows empty state for zero indicators', async () => {
    renderDashboard(serviceMock({ getIndicators: vi.fn().mockResolvedValue(emptyIndicatorsFixture) }))

    await waitFor(() =>
      expect(screen.getByText('O sistema não possui comandos registrados.')).toBeInTheDocument()
    )
  })

  it('shows load error state', async () => {
    renderDashboard(
      serviceMock({
        getIndicators: vi.fn().mockRejectedValue(new Error('boom')),
        listCommands: vi.fn().mockRejectedValue(new Error('boom'))
      })
    )

    await waitFor(() =>
      expect(screen.getByText('Não foi possível carregar os dados.')).toBeInTheDocument()
    )
  })

  it('searches by command id or external id', async () => {
    const user = userEvent.setup()
    const service = serviceMock()
    renderDashboard(service)

    await user.type(await screen.findByLabelText('Pesquisar Command ID ou External ID'), 'BOLSISTA')
    await user.click(screen.getByRole('button', { name: 'Aplicar' }))

    await waitFor(() =>
      expect(service.listCommands).toHaveBeenLastCalledWith(
        expect.objectContaining({ search: 'BOLSISTA' }),
        expect.any(Object),
        expect.any(Object)
      )
    )
  })

  it('opens command details from the table', async () => {
    const user = userEvent.setup()
    renderDashboard()

    const detailButtons = await screen.findAllByRole('button', { name: 'Visualizar detalhes' })
    await user.click(detailButtons[0])

    await waitFor(() => expect(screen.getAllByText(commandDetailFixture.command_id).length).toBeGreaterThan(1))
    expect(screen.getByText('Payload Original')).toBeInTheDocument()
  })

  it('refreshes indicators and list without resetting criteria', async () => {
    const user = userEvent.setup()
    const service = serviceMock()
    renderDashboard(service)

    await user.type(await screen.findByLabelText('Pesquisar Command ID ou External ID'), 'BOLSISTA')
    await user.click(screen.getByRole('button', { name: 'Aplicar' }))
    await user.click(screen.getByRole('button', { name: 'Atualizar dashboard' }))

    await waitFor(() => expect(service.getIndicators).toHaveBeenCalledTimes(2))
    expect(service.listCommands).toHaveBeenLastCalledWith(
      expect.objectContaining({ search: 'BOLSISTA' }),
      expect.any(Object),
      expect.any(Object)
    )
  })
})
