<!-- GPC SHARED — PageHeader. Header sticky: nút back + icon + tiêu đề + slot actions. -->
<template>
  <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-20">
    <button v-if="back !== false" class="text-gray-500 hover:text-gray-800" @click="goBack">
      <FeatherIcon name="arrow-left" class="h-5 w-5" />
    </button>
    <FeatherIcon v-if="icon" :name="icon" class="h-5 w-5 shrink-0" :class="iconClass" />
    <div class="flex-1 min-w-0">
      <h1 class="text-lg font-bold truncate leading-tight">{{ title }}</h1>
      <p v-if="subtitle" class="text-xs text-gray-500 truncate">{{ subtitle }}</p>
    </div>
    <div class="flex items-center gap-2 shrink-0"><slot /></div>
  </header>
</template>
<script setup>
import { FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'
const props = defineProps({
  title: String,
  subtitle: String,
  icon: String,
  iconClass: { type: String, default: 'text-indigo-600' },
  back: { type: [String, Boolean], default: '/' },
})
const router = useRouter()
function goBack() {
  if (props.back === true) router.back()
  else if (typeof props.back === 'string') router.push(props.back)
}
</script>
