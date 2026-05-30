import axios, { type AxiosInstance } from 'axios'

import type {
  CommandDetail,
  CommandListResponse,
  DashboardFilters,
  DashboardIndicators,
  Pagination,
  Sorting
} from '@/types/command'

export interface DashboardService {
  getIndicators(): Promise<DashboardIndicators>
  listCommands(
    filters: DashboardFilters,
    pagination: Pick<Pagination, 'page' | 'page_size'>,
    sorting: Sorting
  ): Promise<CommandListResponse>
  getCommandDetail(commandId: string): Promise<CommandDetail>
}

type HttpClient = Pick<AxiosInstance, 'get'>

export function createDashboardService(
  client: HttpClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 10000
  })
): DashboardService {
  return {
    async getIndicators() {
      const response = await client.get<DashboardIndicators>('/dashboard/indicators')
      return response.data
    },

    async listCommands(filters, pagination, sorting) {
      const response = await client.get<CommandListResponse>('/dashboard/commands', {
        params: buildListParams(filters, pagination, sorting)
      })
      return response.data
    },

    async getCommandDetail(commandId) {
      const response = await client.get<CommandDetail>(
        `/dashboard/commands/${encodeURIComponent(commandId)}`
      )
      return response.data
    }
  }
}

export function buildListParams(
  filters: DashboardFilters,
  pagination: Pick<Pagination, 'page' | 'page_size'>,
  sorting: Sorting
): Record<string, string | number> {
  const params: Record<string, string | number> = {
    page: pagination.page,
    page_size: pagination.page_size,
    sort_by: sorting.sort_by,
    sort_direction: sorting.sort_direction
  }

  for (const [key, value] of Object.entries(filters)) {
    if (value !== '') {
      params[key] = value
    }
  }

  return params
}

let dashboardService: DashboardService = createDashboardService()

export function getDashboardService(): DashboardService {
  return dashboardService
}

export function setDashboardService(service: DashboardService): void {
  dashboardService = service
}
