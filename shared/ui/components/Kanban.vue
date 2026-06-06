<!-- GPC SHARED — Kanban. Cột kéo-thả theo groupKey. Slot card({item}) để render thẻ.
  columns: [{key,label,color}] (color = class viền/dot, vd 'blue'). @move({item,from,to}), @card-click(item). -->
<template>
  <div class="flex gap-3 pb-4 overflow-x-auto">
    <div v-for="col in columns" :key="col.key" class="flex-1 min-w-[230px] max-w-[340px] flex flex-col"
      @dragover.prevent="overCol = col.key" @dragleave="overCol === col.key && (overCol = null)" @drop="onDrop(col.key)">
      <div class="flex items-center gap-2 px-2 py-2 sticky top-0">
        <span class="w-2.5 h-2.5 rounded-full" :class="dotCls(col.color)" />
        <span class="font-semibold text-sm">{{ col.label }}</span>
        <span class="ml-auto text-xs bg-gray-200 text-gray-600 rounded-full px-2 py-0.5">{{ grouped[col.key]?.length || 0 }}</span>
      </div>
      <div class="flex-1 space-y-2 p-1 rounded-xl transition-colors min-h-[60px]"
        :class="overCol === col.key ? 'bg-indigo-50/60 ring-2 ring-indigo-200 ring-dashed' : ''">
        <div v-for="it in grouped[col.key]" :key="it[cardKey]" draggable="true"
          class="app-card p-3 cursor-grab active:cursor-grabbing" :class="dragItem === it ? 'opacity-40' : ''"
          @dragstart="dragItem = it; dragFrom = col.key" @dragend="dragItem = null"
          @click="$emit('card-click', it)">
          <slot name="card" :item="it">{{ it[cardKey] }}</slot>
        </div>
        <div v-if="!(grouped[col.key] && grouped[col.key].length)" class="text-xs text-gray-300 text-center py-4">—</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
const props = defineProps({
  columns: { type: Array, required: true },
  items: { type: Array, default: () => [] },
  groupKey: { type: String, default: 'status' },
  cardKey: { type: String, default: 'name' },
})
const emit = defineEmits(['move', 'card-click'])
const dragItem = ref(null)
const dragFrom = ref(null)
const overCol = ref(null)

const grouped = computed(() => {
  const g = {}
  for (const c of props.columns) g[c.key] = []
  for (const it of props.items) {
    const k = it[props.groupKey]
    if (g[k]) g[k].push(it); else (g.__other__ ||= []).push(it)
  }
  return g
})
const DOTS = { blue: 'bg-blue-500', amber: 'bg-amber-500', purple: 'bg-violet-500', orange: 'bg-orange-500', green: 'bg-emerald-500', red: 'bg-rose-500', gray: 'bg-gray-400', indigo: 'bg-indigo-500' }
function dotCls(c) { return DOTS[c] || c || DOTS.gray }
function onDrop(toCol) {
  overCol.value = null
  const it = dragItem.value, from = dragFrom.value
  dragItem.value = null; dragFrom.value = null
  if (it && from !== toCol) emit('move', { item: it, from, to: toCol })
}
</script>
