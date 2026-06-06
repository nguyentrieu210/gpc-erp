<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.push('/projects')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
        <h1 class="text-lg font-semibold text-gray-900 truncate">{{ proj?.project_name || 'Chi tiết' }}</h1>
      </div>
    </header>
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="proj" class="p-4 space-y-4 max-w-4xl mx-auto">
        <div class="rounded-lg border bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <Badge variant="subtle" :theme="statusTheme(proj.status)" :label="statusLabel(proj.status)" />
            <span v-if="proj.priority" class="text-xs px-2 py-0.5 rounded-full bg-gray-100">{{ proj.priority }}</span>
          </div>
          <div class="mb-3">
            <div class="flex items-center justify-between text-sm mb-1"><span class="text-gray-500">Tiến độ</span><span class="font-medium">{{ proj.percent_complete || 0 }}%</span></div>
            <div class="h-2.5 rounded-full bg-gray-200 overflow-hidden"><div class="h-full rounded-full transition-all" :class="progressColor(proj.percent_complete)" :style="{ width: (proj.percent_complete || 0) + '%' }"></div></div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <div><span class="text-gray-500">Bắt đầu</span><div class="font-medium">{{ $fmtDate(proj.expected_start_date) || '-' }}</div></div>
            <div><span class="text-gray-500">Kết thúc</span><div class="font-medium">{{ $fmtDate(proj.expected_end_date) || '-' }}</div></div>
            <div><span class="text-gray-500">Khách hàng</span><div class="font-medium">{{ proj.customer || '-' }}</div></div>
            <div><span class="text-gray-500">Task</span><div class="font-medium">{{ proj.completed_tasks }}/{{ proj.task_count }}</div></div>
          </div>
        </div>
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="flex border-b">
            <button v-for="t in ['list','kanban']" :key="t" @click="tab = t; if (t==='kanban' && !kanban.length) fetchKanban()" class="flex-1 py-2.5 text-sm font-medium border-b-2 transition" :class="tab === t ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-gray-500'">{{ t === 'list' ? '📋 Danh sách' : '📌 Kanban' }}</button>
          </div>
          <div v-if="tab === 'list'" class="divide-y">
            <div v-if="!proj.tasks?.length" class="py-10 text-center text-gray-400">Chưa có task</div>
            <div v-for="t in proj.tasks" :key="t.name" class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer" @click="$router.push('/tasks/' + t.name)">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2"><span class="font-medium text-gray-900 truncate">{{ t.subject }}</span><Badge :theme="taskStatusTheme(t.status)" :label="taskStatusLabel(t.status)" /><Badge v-if="t.priority==='High'||t.priority==='Urgent'" variant="subtle" theme="red" :label="t.priority" /></div>
                <div class="text-xs text-gray-500 mt-0.5"><span v-if="t.exp_end_date">{{ $fmtDate(t.exp_end_date) }}</span></div>
              </div>
              <span class="ml-2 text-xs text-gray-400">{{ t.progress||0 }}% <FeatherIcon name="chevron-right" class="h-3 w-3 inline" /></span>
            </div>
          </div>
          <div v-if="tab === 'kanban'" class="p-3 overflow-x-auto bg-gray-50">
            <div v-if="kanbanLoading" class="py-10 text-center"><LoadingIndicator /></div>
            <div v-else class="flex gap-3" style="min-width:800px">
              <div v-for="col in kanban" :key="col.key" class="flex-1 min-w-[190px] rounded-lg bg-gray-100/60 p-2"
                @dragover="onDragOver" @drop="onDrop($event, col.key)">
                <div class="flex items-center gap-2 mb-3 px-1">
                  <span class="w-2.5 h-2.5 rounded-full" :class="colHeaderColor(col.key)"></span>
                  <span class="text-xs font-semibold uppercase text-gray-600 flex-1">{{ col.label }}</span>
                  <span class="text-xs bg-white rounded-full px-2 py-0.5 font-medium text-gray-500 shadow-sm">{{ col.tasks.length }}</span>
                </div>
                <div class="space-y-2">
                  <div v-for="t in col.tasks" :key="t.name"
                    class="rounded-lg border bg-white p-3 shadow-sm hover:shadow-md transition cursor-grab active:cursor-grabbing text-sm"
                    :class="{ 'opacity-50': dragTask?.name === t.name }"
                    draggable="true"
                    @dragstart="onDragStart($event, t)"
                    @click="$router.push('/tasks/' + t.name)">
                    <div class="font-medium text-gray-900 line-clamp-2 mb-1">{{ t.subject }}</div>
                    <div class="flex items-center gap-2 text-xs text-gray-500">
                      <span v-if="t.priority" class="px-1.5 py-0.5 rounded text-xs" :class="priorityBadge(t.priority)">{{ t.priority }}</span>
                    </div>
                    <div v-if="t.exp_end_date" class="text-xs mt-2" :class="isOverdue(t)?'text-red-500':'text-gray-400'">
                      <FeatherIcon name="calendar" class="h-3 w-3 inline" /> {{ $fmtDate(t.exp_end_date) }}
                    </div>
                  </div>
                  <div v-if="!col.tasks.length" class="text-xs text-center text-gray-400 py-6">Trống</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { frappeRequest, Button, Badge, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const route = useRoute()
const tab = ref('list')
const dragTask = ref(null)

const { data: proj, loading, error, fetch: fetchProjectApi } = useFrappeApi('duan.api.get_project_detail', { auto: false })
const { loading: kanbanLoading, fetch: fetchKanbanApi } = useFrappeApi('duan.api.get_tasks_by_status', { auto: false })

const kanban = ref([])

onMounted(fetchProject)

async function fetchProject() {
  await fetchProjectApi({ name: route.params.id }).catch(() => {})
}

async function fetchKanban() {
  try {
    const raw = await fetchKanbanApi({ project: route.params.id }) || {}
    const map = { Open: 'Mở', Working: 'Đang làm', 'Pending Review': 'Chờ duyệt', Completed: 'Xong' }
    kanban.value = ['Open', 'Working', 'Pending Review', 'Completed'].map(k => ({ key: k, label: map[k] || k, tasks: raw[k] || [] }))
  } catch (e) { /* ignore */ }
}

async function moveTask(task, toStatus) {
  if (task.status === toStatus) return
  const fromCol = kanban.value.find(c => c.key === task.status)
  const toCol = kanban.value.find(c => c.key === toStatus)
  if (!fromCol || !toCol) return
  // Optimistic update
  fromCol.tasks = fromCol.tasks.filter(t => t.name !== task.name)
  toCol.tasks.push({ ...task, status: toStatus })
  try {
    await frappeRequest({ url: 'duan.api.update_task_status', method: 'POST', params: { name: task.name, status: toStatus } })
  } catch {
    // Rollback: refresh kanban
    fetchKanban()
  }
}

function onDragStart(e, task) { dragTask.value = task; e.dataTransfer.effectAllowed = 'move' }
function onDragOver(e) { e.preventDefault(); e.dataTransfer.dropEffect = 'move' }
function onDrop(e, status) {
  e.preventDefault()
  if (dragTask.value) { moveTask(dragTask.value, status); dragTask.value = null }
}

function isOverdue(t) { if (!t.exp_end_date || t.status === 'Completed') return false; return new Date(t.exp_end_date) < new Date() }
function statusLabel(s) { const m = { Open: 'Mở', Working: 'Đang làm', Completed: 'Xong', Hold: 'Tạm dừng' }; return m[s] || s || 'Mở' }
function statusTheme(s) { const m = { Open: 'blue', Working: 'orange', Completed: 'green', Overdue: 'red', Hold: 'gray' }; return m[s] || 'gray' }
function taskStatusLabel(s) { const m = { Open: 'Mở', Working: 'Đang làm', 'Pending Review': 'Chờ duyệt', Completed: 'Xong' }; return m[s] || s }
function taskStatusTheme(s) { const m = { Open: 'blue', Working: 'orange', 'Pending Review': 'purple', Completed: 'green' }; return m[s] || 'gray' }
function colHeaderColor(s) { const m = { Open: 'bg-blue-500', Working: 'bg-amber-500', 'Pending Review': 'bg-purple-500', Completed: 'bg-green-500' }; return m[s] || 'bg-gray-400' }
function progressColor(pct) { const v = pct || 0; if (v >= 100) return 'bg-green-500'; if (v >= 50) return 'bg-cyan-500'; if (v > 0) return 'bg-amber-500'; return 'bg-gray-300' }
function priorityBadge(p) { const m = { Low: 'bg-gray-100 text-gray-600', Medium: 'bg-blue-50 text-blue-600', High: 'bg-red-50 text-red-600', Urgent: 'bg-red-100 text-red-700' }; return m[p] || 'bg-gray-100' }
</script>
