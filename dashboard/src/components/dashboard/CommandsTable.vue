<script setup lang="ts">
import type {
  CommandListItem,
  Pagination,
  SortDirection,
  SortField,
  Sorting
} from '@/types/command'

const props = defineProps<{
  commands: CommandListItem[]
  pagination: Pagination
  sorting: Sorting
  loading: boolean
}>()

const emit = defineEmits<{
  pageChange: [pagination: Partial<Pagination>]
  sortChange: [sorting: Sorting]
  viewDetails: [commandId: string]
}>()

const sortableColumns: Array<{ field: SortField; label: string }> = [
  { field: 'request_received_at', label: 'Recebido em' },
  { field: 'processing_started_at', label: 'Início' },
  { field: 'processing_finished_at', label: 'Finalizado em' },
  { field: 'status', label: 'Status' },
  { field: 'type', label: 'Type' }
]

function sortBy(field: SortField) {
  const direction: SortDirection =
    props.sorting.sort_by === field && props.sorting.sort_direction === 'desc' ? 'asc' : 'desc'
  emit('sortChange', { sort_by: field, sort_direction: direction })
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '-'
  }
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'medium'
  }).format(new Date(value))
}

function statusClass(status: string): string {
  if (status === 'completed' || status === 'sent') return 'bg-green-50 text-green-800 ring-green-200'
  if (status === 'failed') return 'bg-red-50 text-red-800 ring-red-200'
  if (status === 'queued' || status === 'processing' || status === 'pending') return 'bg-amber-50 text-amber-800 ring-amber-200'
  return 'bg-slate-50 text-slate-700 ring-slate-200'
}

const pageCount = () => Math.max(1, Math.ceil(props.pagination.total / props.pagination.page_size))
</script>

<template>
  <section class="overflow-hidden rounded-md border border-line bg-white shadow-subtle" aria-labelledby="commands-table-title">
    <div class="flex flex-col gap-3 border-b border-line px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 id="commands-table-title" class="text-lg font-semibold text-ink">Comandos</h2>
      <label class="flex items-center gap-2 text-sm text-slate-600">
        <span>Linhas</span>
        <select
          class="rounded-md border border-line px-2 py-1"
          :value="pagination.page_size"
          :disabled="loading"
          @change="emit('pageChange', { page: 1, page_size: Number(($event.target as HTMLSelectElement).value) })"
        >
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </label>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-line text-sm">
        <thead class="bg-panel text-left text-xs font-semibold uppercase text-slate-600">
          <tr>
            <th class="px-4 py-3">Command ID</th>
            <th class="px-4 py-3">
              <button type="button" class="font-semibold" @click="sortBy('type')">Type</button>
            </th>
            <th class="px-4 py-3">External ID</th>
            <th class="px-4 py-3">
              <button type="button" class="font-semibold" @click="sortBy('status')">Status</button>
            </th>
            <th class="px-4 py-3">Callback Status</th>
            <th v-for="column in sortableColumns.slice(0, 3)" :key="column.field" class="px-4 py-3">
              <button type="button" class="font-semibold" @click="sortBy(column.field)">
                {{ column.label }}
              </button>
            </th>
            <th class="px-4 py-3">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-line">
          <tr v-for="command in commands" :key="command.command_id" class="hover:bg-slate-50">
            <td class="max-w-60 truncate px-4 py-3 font-mono text-xs" :title="command.command_id">{{ command.command_id }}</td>
            <td class="px-4 py-3 font-medium">{{ command.type }}</td>
            <td class="px-4 py-3">{{ command.external_id || '-' }}</td>
            <td class="px-4 py-3">
              <span class="inline-flex rounded-full px-2 py-1 text-xs font-semibold ring-1" :class="statusClass(command.status)">
                {{ command.status }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span class="inline-flex rounded-full px-2 py-1 text-xs font-semibold ring-1" :class="statusClass(command.callback_status)">
                {{ command.callback_status }}
              </span>
            </td>
            <td class="px-4 py-3">{{ formatDate(command.request_received_at) }}</td>
            <td class="px-4 py-3">{{ formatDate(command.processing_started_at) }}</td>
            <td class="px-4 py-3">{{ formatDate(command.processing_finished_at) }}</td>
            <td class="px-4 py-3">
              <button type="button" class="rounded-md border border-line px-3 py-1 text-xs font-semibold text-ink hover:bg-panel" @click="emit('viewDetails', command.command_id)">
                Visualizar detalhes
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-col gap-3 border-t border-line px-4 py-3 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
      <span>Página {{ pagination.page }} de {{ pageCount() }} · {{ pagination.total }} registros</span>
      <div class="flex gap-2">
        <button type="button" class="rounded-md border border-line px-3 py-1 font-semibold disabled:opacity-50" :disabled="loading || pagination.page <= 1" @click="emit('pageChange', { page: pagination.page - 1 })">
          Anterior
        </button>
        <button type="button" class="rounded-md border border-line px-3 py-1 font-semibold disabled:opacity-50" :disabled="loading || pagination.page >= pageCount()" @click="emit('pageChange', { page: pagination.page + 1 })">
          Próxima
        </button>
      </div>
    </div>
  </section>
</template>
