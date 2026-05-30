<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string
  }>(),
  {
    message: 'Não foi possível carregar os dados.'
  }
)
</script>

<template>
  <div class="rounded-md border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-800" role="alert">
    {{ message }}
  </div>
</template>
