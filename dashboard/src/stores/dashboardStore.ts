import { defineStore } from 'pinia'

import { getDashboardService } from '@/services/dashboardService'
import {
  defaultFilters,
  defaultPagination,
  defaultSorting,
  emptyIndicators,
  type CommandDetail,
  type CommandListItem,
  type DashboardFilters,
  type DashboardIndicators,
  type Pagination,
  type Sorting
} from '@/types/command'

const LOAD_ERROR = 'Não foi possível carregar os dados.'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    indicators: null as DashboardIndicators | null,
    commands: [] as CommandListItem[],
    filters: defaultFilters(),
    pagination: defaultPagination(),
    sorting: defaultSorting(),
    selectedCommand: null as CommandDetail | null,
    isLoadingIndicators: false,
    isLoadingCommands: false,
    isLoadingDetails: false,
    errorMessage: null as string | null
  }),

  getters: {
    isEmpty(state): boolean {
      return Boolean(state.indicators && state.indicators.total_commands === 0)
    },
    hasNoCommandResults(state): boolean {
      return !state.isLoadingCommands && state.commands.length === 0
    },
    hasActiveLoad(state): boolean {
      return state.isLoadingIndicators || state.isLoadingCommands || state.isLoadingDetails
    },
    indicatorValues(state): DashboardIndicators {
      return state.indicators ?? emptyIndicators()
    }
  },

  actions: {
    clearError() {
      this.errorMessage = null
    },

    async loadIndicators() {
      this.isLoadingIndicators = true
      this.errorMessage = null
      try {
        this.indicators = await getDashboardService().getIndicators()
      } catch {
        this.errorMessage = LOAD_ERROR
      } finally {
        this.isLoadingIndicators = false
      }
    },

    async loadCommands() {
      this.isLoadingCommands = true
      this.errorMessage = null
      try {
        const result = await getDashboardService().listCommands(
          this.filters,
          this.pagination,
          this.sorting
        )
        this.commands = result.items
        this.pagination = {
          page: result.page,
          page_size: result.page_size,
          total: result.total
        }
      } catch {
        this.errorMessage = LOAD_ERROR
      } finally {
        this.isLoadingCommands = false
      }
    },

    async loadCommandDetail(commandId: string) {
      this.isLoadingDetails = true
      this.errorMessage = null
      try {
        this.selectedCommand = await getDashboardService().getCommandDetail(commandId)
      } catch {
        this.errorMessage = LOAD_ERROR
      } finally {
        this.isLoadingDetails = false
      }
    },

    closeDetails() {
      this.selectedCommand = null
    },

    async setFilters(filters: Partial<DashboardFilters>) {
      this.filters = { ...this.filters, ...filters }
      this.pagination.page = 1
      await this.loadCommands()
    },

    async resetFilters() {
      this.filters = defaultFilters()
      this.pagination.page = 1
      await this.loadCommands()
    },

    async setPagination(pagination: Partial<Pagination>) {
      this.pagination = { ...this.pagination, ...pagination }
      await this.loadCommands()
    },

    async setSorting(sorting: Sorting) {
      this.sorting = sorting
      this.pagination.page = 1
      await this.loadCommands()
    },

    async refreshDashboard() {
      this.errorMessage = null
      const previousIndicators = this.indicators
      const previousCommands = this.commands
      const previousPagination = this.pagination
      await this.loadIndicators()
      await this.loadCommands()
      if (this.errorMessage) {
        this.indicators = this.indicators ?? previousIndicators
        this.commands = this.commands.length > 0 ? this.commands : previousCommands
        this.pagination = this.commands.length > 0 ? this.pagination : previousPagination
      }
    }
  }
})
