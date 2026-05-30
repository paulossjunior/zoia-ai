import { createPinia, setActivePinia } from 'pinia'

import { setDashboardService, type DashboardService } from '@/services/dashboardService'
import { useDashboardStore } from '@/stores/dashboardStore'

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

describe('dashboardStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setDashboardService(serviceMock())
  })

  it('loads indicators, commands, and details', async () => {
    const store = useDashboardStore()

    await store.loadIndicators()
    await store.loadCommands()
    await store.loadCommandDetail(commandDetailFixture.command_id)

    expect(store.indicators).toEqual(indicatorsFixture)
    expect(store.commands).toHaveLength(2)
    expect(store.selectedCommand?.command_id).toBe(commandDetailFixture.command_id)
  })

  it('sets the empty state from zero indicators', async () => {
    setDashboardService(serviceMock({ getIndicators: vi.fn().mockResolvedValue(emptyIndicatorsFixture) }))
    const store = useDashboardStore()

    await store.loadIndicators()

    expect(store.isEmpty).toBe(true)
  })

  it('preserves criteria when refreshing', async () => {
    const service = serviceMock()
    setDashboardService(service)
    const store = useDashboardStore()
    store.filters.search = 'BOLSISTA'
    store.pagination.page = 3

    await store.refreshDashboard()

    expect(service.listCommands).toHaveBeenCalledWith(
      expect.objectContaining({ search: 'BOLSISTA' }),
      expect.objectContaining({ page: 3 }),
      expect.any(Object)
    )
  })

  it('keeps visible data when refresh fails', async () => {
    const store = useDashboardStore()
    store.commands = commandListResponseFixture.items
    store.indicators = indicatorsFixture
    setDashboardService(
      serviceMock({
        getIndicators: vi.fn().mockRejectedValue(new Error('boom')),
        listCommands: vi.fn().mockRejectedValue(new Error('boom'))
      })
    )

    await store.refreshDashboard()

    expect(store.commands).toEqual(commandListResponseFixture.items)
    expect(store.indicators).toEqual(indicatorsFixture)
    expect(store.errorMessage).toBe('Não foi possível carregar os dados.')
  })
})
