<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: number
    tone?: 'neutral' | 'success' | 'warning' | 'danger'
  }>(),
  {
    tone: 'neutral'
  }
)

const toneClasses = {
  neutral: 'border-slate-200 bg-white text-ink',
  success: 'border-green-200 bg-green-50 text-green-900',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
  danger: 'border-red-200 bg-red-50 text-red-900'
}
</script>

<template>
  <article class="rounded-md border p-4 shadow-subtle" :class="toneClasses[tone]">
    <p class="text-sm font-medium text-slate-600">{{ label }}</p>
    <p class="mt-2 text-3xl font-bold tabular-nums">{{ value }}</p>
  </article>
</template>
