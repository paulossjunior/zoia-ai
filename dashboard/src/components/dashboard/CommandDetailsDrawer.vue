<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

import type { CommandDetail } from '@/types/command'

import JsonViewer from './JsonViewer.vue'
import LoadingState from './LoadingState.vue'

defineProps<{
  command: CommandDetail | null
  loading: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

function formatDate(value: string | null | undefined): string {
  if (!value) return '-'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'medium' }).format(new Date(value))
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 bg-slate-950/40" aria-hidden="true" @click="emit('close')" />
    <aside class="fixed right-0 top-0 z-50 flex h-full w-full max-w-3xl flex-col bg-white shadow-xl" role="dialog" aria-modal="true" aria-labelledby="command-detail-title">
      <header class="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <p class="text-xs font-semibold uppercase text-slate-500">Detalhes</p>
          <h2 id="command-detail-title" class="text-xl font-bold text-ink">Comando</h2>
        </div>
        <button type="button" class="rounded-md border border-line px-3 py-1 text-sm font-semibold" aria-label="Fechar detalhes" @click="emit('close')">
          Fechar
        </button>
      </header>

      <div class="flex-1 overflow-y-auto p-5">
        <LoadingState v-if="loading" label="Carregando detalhes..." />
        <div v-else-if="command" class="space-y-5">
          <section class="grid gap-3 rounded-md border border-line p-4 sm:grid-cols-3">
            <div>
              <p class="text-xs font-semibold uppercase text-slate-500">Command ID</p>
              <p class="break-all font-mono text-sm">{{ command.command_id }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase text-slate-500">Type</p>
              <p class="text-sm font-semibold">{{ command.type }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase text-slate-500">External ID</p>
              <p class="text-sm">{{ command.external_id || '-' }}</p>
            </div>
          </section>

          <section class="grid gap-3 rounded-md border border-line p-4 sm:grid-cols-2">
            <div><p class="text-xs font-semibold uppercase text-slate-500">Status</p><p>{{ command.status }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Recebido em</p><p>{{ formatDate(command.request_received_at) }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Início</p><p>{{ formatDate(command.processing_started_at) }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Finalização</p><p>{{ formatDate(command.processing_finished_at) }}</p></div>
          </section>

          <section class="grid gap-3 rounded-md border border-line p-4 sm:grid-cols-2">
            <div><p class="text-xs font-semibold uppercase text-slate-500">Callback URL</p><p class="break-all">{{ command.callback || '-' }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Callback Status</p><p>{{ command.callback_status }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Callback Error Message</p><p>{{ command.callback_error_message || '-' }}</p></div>
            <div><p class="text-xs font-semibold uppercase text-slate-500">Callback Sent At</p><p>{{ formatDate(command.callback_sent_at) }}</p></div>
          </section>

          <JsonViewer label="Payload Original" :value="command.payload" />
          <JsonViewer label="Resposta" :value="command.response_payload" />

          <section class="rounded-md border border-line p-4">
            <p class="text-xs font-semibold uppercase text-slate-500">Error Message</p>
            <p class="mt-1 text-sm">{{ command.error_message || '-' }}</p>
          </section>
        </div>
      </div>
    </aside>
  </Teleport>
</template>
