<script setup lang="ts">
withDefaults(
  defineProps<{
    loading?: boolean
  }>(),
  {
    loading: false
  }
)

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <button
    type="button"
    class="inline-flex min-h-10 items-center gap-2 rounded-md border border-line bg-white px-4 text-sm font-semibold text-ink shadow-subtle transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
    :disabled="loading"
    aria-label="Atualizar dashboard"
    @click="emit('refresh')"
  >
    <span
      class="inline-block h-4 w-4 rounded-full border-2 border-slate-300 border-t-ink"
      :class="{ 'animate-spin': loading }"
      aria-hidden="true"
    />
    {{ loading ? 'Atualizando' : 'Atualizar' }}
  </button>
</template>
