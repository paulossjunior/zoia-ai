<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string
  }>(),
  {
    message: 'O sistema não possui comandos registrados.'
  }
)
</script>

<template>
  <div class="rounded-md border border-dashed border-line bg-white p-8 text-center text-sm text-slate-600">
    {{ message }}
  </div>
</template>
