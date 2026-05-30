<script setup lang="ts">
import type { DashboardIndicators } from '@/types/command'

import IndicatorCard from './IndicatorCard.vue'

defineProps<{
  indicators: DashboardIndicators
}>()
</script>

<template>
  <section aria-labelledby="dashboard-indicators" class="space-y-4">
    <h2 id="dashboard-indicators" class="text-lg font-semibold text-ink">Indicadores</h2>
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
      <IndicatorCard label="Total de comandos" :value="indicators.total_commands" />
      <IndicatorCard label="Total em fila" :value="indicators.queued_commands" tone="warning" />
      <IndicatorCard label="Total em processamento" :value="indicators.processing_commands" tone="warning" />
      <IndicatorCard label="Total concluídos" :value="indicators.completed_commands" tone="success" />
      <IndicatorCard label="Total com falha" :value="indicators.failed_commands" tone="danger" />
      <IndicatorCard label="Total callback not_required" :value="indicators.callback_not_required" />
      <IndicatorCard label="Total callback pending" :value="indicators.callback_pending" tone="warning" />
      <IndicatorCard label="Total callback sent" :value="indicators.callback_sent" tone="success" />
      <IndicatorCard label="Total callback failed" :value="indicators.callback_failed" tone="danger" />
    </div>
  </section>
</template>
