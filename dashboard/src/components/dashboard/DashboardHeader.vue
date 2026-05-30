<script setup lang="ts">
import RefreshButton from './RefreshButton.vue'

defineProps<{
  loading: boolean
}>()

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <header class="flex flex-col gap-4 border-b border-line bg-white px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
    <div>
      <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Operação de comandos</p>
      <h1 class="mt-1 text-2xl font-bold text-ink sm:text-3xl">Dashboard Operacional</h1>
    </div>
    <RefreshButton :loading="loading" @refresh="emit('refresh')" />
  </header>
</template>
