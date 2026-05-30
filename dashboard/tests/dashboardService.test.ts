import { buildListParams, createDashboardService } from '@/services/dashboardService'
import { defaultFilters, defaultPagination, defaultSorting } from '@/types/command'

import {
  commandDetailFixture,
  commandListResponseFixture,
  indicatorsFixture
} from './fixtures'

describe('dashboardService', () => {
  it('calls dashboard read endpoints only', async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({ data: indicatorsFixture })
      .mockResolvedValueOnce({ data: commandListResponseFixture })
      .mockResolvedValueOnce({ data: commandDetailFixture })
    const post = vi.fn()
    const put = vi.fn()
    const patch = vi.fn()
    const del = vi.fn()
    const service = createDashboardService({ get } as never)

    await service.getIndicators()
    await service.listCommands(defaultFilters(), defaultPagination(), defaultSorting())
    await service.getCommandDetail(commandDetailFixture.command_id)

    expect(get).toHaveBeenNthCalledWith(1, '/dashboard/indicators')
    expect(get).toHaveBeenNthCalledWith(2, '/dashboard/commands', expect.any(Object))
    expect(get).toHaveBeenNthCalledWith(3, `/dashboard/commands/${commandDetailFixture.command_id}`)
    expect(post).not.toHaveBeenCalled()
    expect(put).not.toHaveBeenCalled()
    expect(patch).not.toHaveBeenCalled()
    expect(del).not.toHaveBeenCalled()
  })

  it('serializes list filters, search, sorting, and pagination', () => {
    const params = buildListParams(
      {
        ...defaultFilters(),
        status: 'failed',
        type: 'SEND_EMAIL',
        external_id: 'BOLSISTA-123',
        callback_status: 'failed',
        received_from: '2026-05-30T10:00',
        received_to: '2026-05-30T11:00',
        processing_from: '2026-05-30T10:01',
        processing_to: '2026-05-30T10:03',
        search: 'BOLSISTA'
      },
      { page: 2, page_size: 50 },
      { sort_by: 'status', sort_direction: 'asc' }
    )

    expect(params).toMatchObject({
      page: 2,
      page_size: 50,
      status: 'failed',
      type: 'SEND_EMAIL',
      external_id: 'BOLSISTA-123',
      callback_status: 'failed',
      received_from: '2026-05-30T10:00',
      received_to: '2026-05-30T11:00',
      processing_from: '2026-05-30T10:01',
      processing_to: '2026-05-30T10:03',
      search: 'BOLSISTA',
      sort_by: 'status',
      sort_direction: 'asc'
    })
  })
})
