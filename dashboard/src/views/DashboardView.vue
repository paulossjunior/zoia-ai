<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'

import CommandDetailsDrawer from '@/components/dashboard/CommandDetailsDrawer.vue'
import CommandsFilters from '@/components/dashboard/CommandsFilters.vue'
import CommandsTable from '@/components/dashboard/CommandsTable.vue'
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue'
import EmptyState from '@/components/dashboard/EmptyState.vue'
import ErrorState from '@/components/dashboard/ErrorState.vue'
import IndicatorsGrid from '@/components/dashboard/IndicatorsGrid.vue'
import LoadingState from '@/components/dashboard/LoadingState.vue'
import { useDashboardStore } from '@/stores/dashboardStore'
import type { DashboardFilters, Pagination, Sorting } from '@/types/command'

const store = useDashboardStore()
const {
  commands,
  errorMessage,
  filters,
  hasActiveLoad,
  hasNoCommandResults,
  indicatorValues,
  isEmpty,
  isLoadingCommands,
  isLoadingDetails,
  isLoadingIndicators,
  pagination,
  selectedCommand,
  sorting
} = storeToRefs(store)

onMounted(async () => {
  await Promise.all([store.loadIndicators(), store.loadCommands()])
})

async function applyFilters(nextFilters: Partial<DashboardFilters>) {
  await store.setFilters(nextFilters)
}

async function changePage(nextPagination: Partial<Pagination>) {
  await store.setPagination(nextPagination)
}

async function changeSort(nextSorting: Sorting) {
  await store.setSorting(nextSorting)
}

async function openDetails(commandId: string) {
  await store.loadCommandDetail(commandId)
}
</script>

<template>
  <main class="min-h-screen bg-panel">
    <DashboardHeader :loading="hasActiveLoad" @refresh="store.refreshDashboard" />

    <div class="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8">
      <ErrorState v-if="errorMessage" :message="errorMessage" />

      <LoadingState v-if="isLoadingIndicators && !store.indicators" label="Carregando indicadores..." />
      <IndicatorsGrid v-else :indicators="indicatorValues" />

      <EmptyState v-if="isEmpty && !isLoadingIndicators" />

      <section class="space-y-4" aria-labelledby="command-search-title">
        <div>
          <h2 id="command-search-title" class="text-lg font-semibold text-ink">Consulta de comandos</h2>
          <p class="text-sm text-slate-600">Filtros, ordenação e busca consultam apenas dados persistidos.</p>
        </div>

        <CommandsFilters :filters="filters" :loading="isLoadingCommands" @apply="applyFilters" @reset="store.resetFilters" />

        <LoadingState v-if="isLoadingCommands && commands.length === 0" label="Carregando comandos..." />
        <EmptyState v-else-if="hasNoCommandResults" />
        <CommandsTable
          v-else
          :commands="commands"
          :pagination="pagination"
          :sorting="sorting"
          :loading="isLoadingCommands"
          @page-change="changePage"
          @sort-change="changeSort"
          @view-details="openDetails"
        />
      </section>
    </div>

    <CommandDetailsDrawer
      v-if="selectedCommand || isLoadingDetails"
      :command="selectedCommand"
      :loading="isLoadingDetails"
      @close="store.closeDetails"
    />
  </main>
</template>
