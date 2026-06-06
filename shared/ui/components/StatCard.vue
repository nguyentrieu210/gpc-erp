<!-- GPC SHARED — StatCard. Thẻ KPI dashboard: icon + nhãn + số + phụ đề, click điều hướng tùy chọn. -->
<template>
  <div :role="to ? 'button' : undefined" :tabindex="to ? 0 : undefined" @click="to && $router.push(to)"
    @keydown.enter="to && $router.push(to)" @keydown.space.prevent="to && $router.push(to)"
    class="group app-card text-left p-4 flex items-center gap-3 w-full outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
    :class="to ? 'cursor-pointer select-none' : ''">
    <div class="h-11 w-11 rounded-xl flex items-center justify-center shrink-0" :class="toneBg">
      <FeatherIcon v-if="icon" :name="icon" class="h-5 w-5" :class="toneText" />
    </div>
    <div class="min-w-0">
      <div class="text-xs text-gray-500 truncate">{{ label }}</div>
      <div class="text-xl font-bold truncate">{{ value }}</div>
      <div v-if="sub" class="text-xs truncate" :class="subTone">{{ sub }}</div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
const props = defineProps({
  label: String, value: [String, Number], icon: String, sub: String,
  tone: { type: String, default: 'indigo' },
  subTone: { type: String, default: 'text-gray-400' },
  to: String,
})
const BG = { indigo: 'bg-indigo-50', violet: 'bg-violet-50', emerald: 'bg-emerald-50', amber: 'bg-amber-50', rose: 'bg-rose-50', blue: 'bg-blue-50', sky: 'bg-sky-50' }
const TXT = { indigo: 'text-indigo-600', violet: 'text-violet-600', emerald: 'text-emerald-600', amber: 'text-amber-600', rose: 'text-rose-600', blue: 'text-blue-600', sky: 'text-sky-600' }
const toneBg = computed(() => BG[props.tone] || BG.indigo)
const toneText = computed(() => TXT[props.tone] || TXT.indigo)
</script>
