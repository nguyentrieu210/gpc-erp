<!-- GPC SHARED — ActivityTimeline. Dòng thời gian hoạt động (mảng {time,user,action,detail,tone}). -->
<template>
  <div class="space-y-0">
    <div v-if="!items || !items.length" class="text-sm text-gray-400 py-4 text-center">Chưa có hoạt động</div>
    <div v-for="(it, i) in items" :key="i" class="flex gap-3 pb-4 last:pb-0 relative">
      <div class="flex flex-col items-center">
        <span class="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0" :class="dotCls(it.tone)" />
        <span v-if="i < items.length - 1" class="w-px flex-1 bg-gray-200 my-1" />
      </div>
      <div class="min-w-0 flex-1">
        <div class="text-sm font-medium">{{ it.action }}</div>
        <div v-if="it.detail" class="text-xs text-gray-600 whitespace-pre-wrap break-words">{{ it.detail }}</div>
        <div class="text-[11px] text-gray-400 mt-0.5">
          <span v-if="it.time">{{ $fmtDateTime ? $fmtDateTime(it.time) : it.time }}</span>
          <span v-if="it.user"> · {{ it.user }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
defineProps({ items: { type: Array, default: () => [] } })
const DOTS = { green: 'bg-emerald-500', amber: 'bg-amber-500', red: 'bg-rose-500', blue: 'bg-blue-500', gray: 'bg-gray-400', purple: 'bg-violet-500', indigo: 'bg-indigo-500' }
function dotCls(t) { return DOTS[t] || DOTS.indigo }
</script>
