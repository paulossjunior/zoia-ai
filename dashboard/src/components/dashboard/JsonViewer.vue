<script setup lang="ts">
import { computed } from 'vue'

import type { JsonValue } from '@/types/command'

import JsonNode from './JsonNode.vue'

const props = defineProps<{
  value: JsonValue
  label: string
}>()

const serialized = computed(() => JSON.stringify(props.value, null, 2))

async function copyJson() {
  await navigator.clipboard?.writeText(serialized.value)
}
</script>

<template>
  <div class="rounded-md border border-line bg-slate-950 text-slate-100">
    <div class="flex items-center justify-between border-b border-slate-700 px-3 py-2">
      <h3 class="text-sm font-semibold">{{ label }}</h3>
      <button
        type="button"
        class="rounded-md border border-slate-600 px-2 py-1 text-xs font-semibold hover:bg-slate-800"
        @click="copyJson"
      >
        Copiar
      </button>
    </div>

    <pre class="overflow-auto p-3 text-xs leading-6"><JsonNode :value="value" /></pre>
  </div>
</template>
