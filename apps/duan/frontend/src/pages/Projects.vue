<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
        <h1 class="text-lg font-semibold text-gray-900">Tất cả dự án</h1>
      </div>
    </header>
    <div class="border-b bg-white px-4 py-2 flex items-center gap-2">
      <input v-model="search" @input="onSearch" placeholder="Tìm dự án..." class="flex-1 rounded-lg border px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none" />
      <select v-model="statusFilter" @change="fetchData" class="rounded-lg border px-2 py-2 text-sm">
        <option value="">Tất cả</option><option value="Open">Mở</option><option value="Working">Đang làm</option><option value="Completed">Hoàn thành</option>
      </select>
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="!projects.length" class="py-20 text-center text-gray-400"><FeatherIcon name="folder" class="mx-auto mb-2 h-8 w-8" /><p>Không có dự án nào</p></div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="p in projects" :key="p.name" class="rounded-lg border bg-white p-4 shadow-sm hover:shadow-md transition cursor-pointer" @click="$router.push('/projects/' + p.name)">
          <div class="flex items-start justify-between mb-3">
            <h3 class="font-semibold text-gray-900 line-clamp-2 flex-1">{{ p.project_name }}</h3>
            <Badge variant="subtle" :theme="statusTheme(p.status)" :label="statusLabel(p.status)" class="ml-2 flex-shrink-0" />
          </div>
          <div class="mb-3">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1"><span>Tiến độ</span><span>{{ p.percent_complete || 0 }}%</span></div>
            <div class="h-2 rounded-full bg-gray-200 overflow-hidden"><div class="h-full rounded-full transition-all" :class="progressColor(p.percent_complete)" :style="{ width: (p.percent_complete || 0) + '%' }"></div></div>
          </div>
          <div class="flex items-center gap-3 text-xs text-gray-500">
            <span><FeatherIcon name="check-square" class="h-3 w-3 inline" /> {{ p.task_count || 0 }} task</span>
            <span v-if="p.expected_end_date"><FeatherIcon name="calendar" class="h-3 w-3 inline" /> {{ $fmtDate(p.expected_end_date) }}</span>
          </div>
          <div v-if="p.overdue_tasks > 0" class="mt-2 text-xs text-red-500"><FeatherIcon name="alert-triangle" class="h-3 w-3 inline" /> {{ p.overdue_tasks }} quá hạn</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, Badge, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const search = ref('')
const statusFilter = ref('')

const { data: projects, loading, error, fetch: fetchProjects } = useFrappeApi('duan.api.get_projects', {
  auto: false,
  initialData: [],
})

async function fetchData() {
  const p = { search: search.value, page_length: '50' }
  if (statusFilter.value) p.status = statusFilter.value
  await fetchProjects(p)
}

let timer = null
function onSearch() { clearTimeout(timer); timer = setTimeout(fetchData, 300) }
onMounted(fetchData)

function statusLabel(s) { const m = { Open: 'Mở', Working: 'Đang làm', Completed: 'Xong', Hold: 'Tạm dừng' }; return m[s] || s || 'Mở' }
function statusTheme(s) { const m = { Open: 'blue', Working: 'orange', Completed: 'green', Overdue: 'red', Hold: 'gray' }; return m[s] || 'gray' }
function progressColor(pct) { const v = pct || 0; if (v >= 100) return 'bg-green-500'; if (v >= 50) return 'bg-cyan-500'; if (v > 0) return 'bg-amber-500'; return 'bg-gray-300' }
</script>
