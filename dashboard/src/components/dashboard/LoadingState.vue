<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
  }>(),
  {
    label: 'Carregando dados...'
  }
)
</script>

<template>
  <div class="flex min-h-24 items-center justify-center rounded-md border border-line bg-white p-6 text-sm text-slate-600" role="status">
    <span class="mr-3 h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-ink" aria-hidden="true" />
    {{ label }}
  </div>
</template>
