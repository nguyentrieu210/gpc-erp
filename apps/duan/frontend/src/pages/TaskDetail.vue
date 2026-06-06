<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="goBack"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
        <h1 class="text-lg font-semibold text-gray-900 truncate">{{ task?.subject || 'Chi tiết task' }}</h1>
      </div>
    </header>
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="task" class="p-4 space-y-4 max-w-3xl mx-auto">
        <div class="rounded-lg border bg-white p-4 shadow-sm">
          <div class="flex items-center gap-2 mb-3">
            <Badge :theme="taskStatusTheme(task.status)" :label="taskStatusLabel(task.status)" />
            <Badge v-if="task.priority" variant="subtle" :theme="task.priority==='High'||task.priority==='Urgent'?'red':'blue'" :label="task.priority" />
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
            <div><span class="text-gray-500">Dự án</span><div class="font-medium"><router-link v-if="task.project" :to="'/projects/'+task.project" class="text-cyan-600 hover:underline">{{ task.project }}</router-link><span v-else>-</span></div></div>
            <div><span class="text-gray-500">Hết hạn</span><div class="font-medium" :class="isOverdue?'text-red-600':''">{{ $fmtDate(task.exp_end_date) || '-' }}</div></div>
            <div><span class="text-gray-500">Tiến độ</span><div class="flex items-center gap-2"><div class="flex-1 h-1.5 rounded-full bg-gray-200 overflow-hidden"><div class="h-full rounded-full" :class="progressColor(task.progress)" :style="{width:(task.progress||0)+'%'}"></div></div><span class="text-xs">{{ task.progress||0 }}%</span></div></div>
            <div><span class="text-gray-500">Bắt đầu</span><div class="font-medium">{{ $fmtDate(task.exp_start_date) || '-' }}</div></div>
            <div><span class="text-gray-500">Thời gian</span><div class="font-medium">{{ task.actual_time || '0' }}h</div></div>
          </div>
        </div>
        <div v-if="task.description" class="rounded-lg border bg-white p-4 shadow-sm">
          <h3 class="font-medium text-gray-900 mb-2">Mô tả</h3>
          <div class="prose prose-sm text-gray-600" v-html="task.description"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const route = useRoute()
const router = useRouter()

const { data: task, loading, error, fetch: fetchTask } = useFrappeApi('duan.api.get_task_detail', { auto: false })

onMounted(async () => {
  await fetchTask({ name: route.params.id })
})

const isOverdue = computed(() => {
  if (!task.value?.exp_end_date || task.value?.status === 'Completed') return false
  return new Date(task.value.exp_end_date) < new Date()
})

function goBack() { router.push(task.value?.project ? '/projects/' + task.value.project : '/') }
function taskStatusLabel(s) { const m = { Open: 'Mở', Working: 'Đang làm', 'Pending Review': 'Chờ duyệt', Completed: 'Xong' }; return m[s] || s }
function taskStatusTheme(s) { const m = { Open: 'blue', Working: 'orange', 'Pending Review': 'purple', Completed: 'green' }; return m[s] || 'gray' }
function progressColor(pct) { const v = pct || 0; if (v >= 100) return 'bg-green-500'; if (v >= 50) return 'bg-cyan-500'; if (v > 0) return 'bg-amber-500'; return 'bg-gray-300' }
</script>
