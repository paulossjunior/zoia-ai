<script setup lang="ts">
import { computed, shallowRef } from 'vue'

import type { JsonValue } from '@/types/command'

const props = defineProps<{
  value: JsonValue
  name?: string
}>()

const collapsed = shallowRef(false)

const isObject = computed(() => props.value !== null && typeof props.value === 'object')
const isArray = computed(() => Array.isArray(props.value))
const childEntries = computed<Array<[string, JsonValue]>>(() => {
  if (Array.isArray(props.value)) {
    return props.value.map((item, index) => [String(index), item])
  }
  if (props.value !== null && typeof props.value === 'object') {
    return Object.entries(props.value)
  }
  return []
})

const primitiveValue = computed(() => {
  if (typeof props.value === 'string') return `"${props.value}"`
  return String(props.value)
})

const opener = computed(() => (isArray.value ? '[' : '{'))
const closer = computed(() => (isArray.value ? ']' : '}'))
</script>

<template>
  <span>
    <span v-if="name" class="text-sky-200">{{ isArray ? `${name}: ` : `"${name}": ` }}</span>
    <span v-if="!isObject" class="text-emerald-200">{{ primitiveValue }}</span>
    <span v-else>
      <button
        type="button"
        class="mr-1 text-slate-300 hover:text-white"
        :aria-label="collapsed ? 'Expandir JSON' : 'Recolher JSON'"
        @click="collapsed = !collapsed"
      >
        {{ collapsed ? '+' : '-' }}
      </button>
      <span>{{ opener }}</span>
      <span v-if="collapsed"> {{ childEntries.length }} item{{ childEntries.length === 1 ? '' : 's' }} {{ closer }}</span>
      <span v-else>
        <span v-for="([key, child], index) in childEntries" :key="key" class="block pl-4">
          <JsonNode :name="key" :value="child" />
          <span v-if="index < childEntries.length - 1">,</span>
        </span>
        <span class="block">{{ closer }}</span>
      </span>
    </span>
  </span>
</template>
