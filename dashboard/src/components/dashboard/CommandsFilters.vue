<script setup lang="ts">
import { reactive, watch } from 'vue'

import {
  callbackStatuses,
  commandStatuses,
  type DashboardFilters
} from '@/types/command'

const props = defineProps<{
  filters: DashboardFilters
  loading: boolean
}>()

const emit = defineEmits<{
  apply: [filters: Partial<DashboardFilters>]
  reset: []
}>()

const localFilters = reactive<DashboardFilters>({ ...props.filters })

watch(
  () => props.filters,
  (filters) => {
    Object.assign(localFilters, filters)
  },
  { deep: true }
)

function applyFilters() {
  emit('apply', { ...localFilters })
}
</script>

<template>
  <form class="rounded-md border border-line bg-white p-4 shadow-subtle" @submit.prevent="applyFilters">
    <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Status</span>
        <select v-model="localFilters.status" class="w-full rounded-md border border-line px-3 py-2">
          <option value="">Todos</option>
          <option v-for="status in commandStatuses" :key="status" :value="status">{{ status }}</option>
        </select>
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Type</span>
        <input v-model.trim="localFilters.type" class="w-full rounded-md border border-line px-3 py-2" placeholder="TEST_COMMAND" />
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>External ID</span>
        <input v-model.trim="localFilters.external_id" class="w-full rounded-md border border-line px-3 py-2" placeholder="BOLSISTA-12345" />
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Callback Status</span>
        <select v-model="localFilters.callback_status" class="w-full rounded-md border border-line px-3 py-2">
          <option value="">Todos</option>
          <option v-for="status in callbackStatuses" :key="status" :value="status">{{ status }}</option>
        </select>
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Recebido de</span>
        <input v-model="localFilters.received_from" type="datetime-local" class="w-full rounded-md border border-line px-3 py-2" />
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Recebido até</span>
        <input v-model="localFilters.received_to" type="datetime-local" class="w-full rounded-md border border-line px-3 py-2" />
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Processamento de</span>
        <input v-model="localFilters.processing_from" type="datetime-local" class="w-full rounded-md border border-line px-3 py-2" />
      </label>

      <label class="space-y-1 text-sm font-medium text-slate-700">
        <span>Processamento até</span>
        <input v-model="localFilters.processing_to" type="datetime-local" class="w-full rounded-md border border-line px-3 py-2" />
      </label>
    </div>

    <div class="mt-4 flex flex-col gap-3 lg:flex-row lg:items-end">
      <label class="flex-1 space-y-1 text-sm font-medium text-slate-700">
        <span>Pesquisar Command ID ou External ID</span>
        <input v-model.trim="localFilters.search" class="w-full rounded-md border border-line px-3 py-2" placeholder="ID do comando ou external id" />
      </label>
      <div class="flex gap-2">
        <button type="submit" class="rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" :disabled="loading">
          Aplicar
        </button>
        <button type="button" class="rounded-md border border-line px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60" :disabled="loading" @click="emit('reset')">
          Limpar
        </button>
      </div>
    </div>
  </form>
</template>
