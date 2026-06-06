<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Chấm công</h1>
      <Button size="sm" variant="subtle" @click="exportGrid" :loading="exporting"><FeatherIcon name="download" class="h-4 w-4" /> Xuất Excel</Button>
      <input type="month" v-model="period" @change="loadGrid" class="text-sm border rounded-lg px-2 py-1.5" />
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-full mx-auto space-y-4">

        <!-- Stats -->
        <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-indigo-600">{{ grid.total || 0 }}</div><div class="text-[10px] text-gray-500">Nhân viên</div></div>
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-green-600">{{ totals.present }}</div><div class="text-[10px] text-gray-500">Đi làm</div></div>
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-red-600">{{ totals.absent }}</div><div class="text-[10px] text-gray-500">Vắng</div></div>
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-amber-600">{{ totals.late }}</div><div class="text-[10px] text-gray-500">Đi muộn</div></div>
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-cyan-600">{{ totals.hours }}</div><div class="text-[10px] text-gray-500">Tổng giờ</div></div>
          <div class="rounded-lg bg-white border p-2 text-center"><div class="text-lg font-bold text-gray-600">{{ grid.month }}</div><div class="text-[10px] text-gray-500">Kỳ</div></div>
        </div>

        <!-- Filter -->
        <div class="flex items-center gap-2 flex-wrap">
          <input v-model="search" @input="debouncedSearch" placeholder="🔍 Tìm NV..." class="text-sm border rounded-lg px-3 py-2 max-w-[200px]" />
          <select v-model="filterDept" @change="loadGrid" class="text-sm border rounded-lg px-2 py-2">
            <option value="">Tất cả phòng ban</option>
            <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>

        <!-- Grid table -->
        <div class="rounded-lg border bg-white shadow-sm overflow-hidden">
          <div v-if="gridLoading" class="flex items-center justify-center py-16"><LoadingIndicator /></div>
          <div v-else-if="!gridData.length" class="text-center text-gray-400 py-16">Chưa có dữ liệu chấm công tháng {{ grid.month }}</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-[11px] border-collapse">
              <thead>
                <tr class="bg-gray-50/70 sticky top-0">
                  <th class="sticky left-0 bg-gray-50/70 text-left px-2 py-2 border-b z-10" style="min-width:120px">Nhân viên</th>
                  <th v-for="d in grid.days" :key="d" class="text-center px-0.5 py-1 border-b font-mono" style="min-width:26px;max-width:30px" :class="isWeekend(d) ? 'bg-red-50/30' : ''">{{ d }}</th>
                  <th class="text-center px-2 py-1 border-b bg-green-50/30">CC</th>
                  <th class="text-center px-2 py-1 border-b bg-red-50/30">V</th>
                  <th class="text-center px-2 py-1 border-b bg-amber-50/30">ĐM</th>
                  <th class="text-center px-2 py-1 border-b">Giờ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in filteredData" :key="r.name" class="hover:bg-gray-50 border-b">
                  <td class="sticky left-0 bg-white px-2 py-1 font-medium text-gray-800 truncate" style="max-width:120px">
                    <div>{{ r.employee_name }}</div>
                    <div class="text-[9px] text-gray-400">{{ r.department?.split(' - ')[0] }}</div>
                  </td>
                  <td v-for="d in grid.days" :key="d" class="text-center px-0.5 py-1" style="min-width:26px;max-width:30px">
                    <span v-if="cell(r, d).s" class="inline-block w-5 h-5 rounded-full text-[9px] leading-5 font-bold"
                      :class="cellColor(cell(r, d))"
                      :title="(cell(r, d).in || '') + (cell(r, d).out ? '→'+cell(r, d).out : '')"
                    >{{ cellIcon(cell(r, d)) }}</span>
                  </td>
                  <td class="text-center font-semibold text-green-700">{{ r.present }}</td>
                  <td class="text-center text-red-500">{{ r.absent || '' }}</td>
                  <td class="text-center text-amber-600">{{ r.late || '' }}</td>
                  <td class="text-center text-gray-600">{{ r.total_hours || '' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const period = ref(new Date().toISOString().slice(0, 7))
const grid = ref({ data: [], days: [], month: '', total: 0 })
const gridLoading = ref(false)
const exporting = ref(false)
const toast = ref('')
const search = ref('')
const filterDept = ref('')
const departments = ref([])

const gridData = computed(() => grid.value.data || [])
const filteredData = computed(() => {
  if (!search.value) return gridData.value
  const q = search.value.toLowerCase()
  return gridData.value.filter(r => (r.employee_name || '').toLowerCase().includes(q) || (r.name || '').toLowerCase().includes(q))
})

const totals = computed(() => {
  let p = 0, a = 0, l = 0, h = 0
  for (const r of gridData.value) {
    p += r.present || 0; a += r.absent || 0; l += r.late || 0; h += r.total_hours || 0
  }
  return { present: p, absent: a, late: l, hours: h.toFixed(0) }
})

function cell(r, day) { return (r['a_' + day]) || {} }
function cellColor(c) {
  if (!c.s) return 'bg-gray-100 text-gray-400'
  if (c.l) return 'bg-amber-200 text-amber-800'
  if (c.s === 'Present') return 'bg-green-200 text-green-800'
  if (c.s === 'Half Day') return 'bg-blue-200 text-blue-800'
  if (c.s === 'Absent') return 'bg-red-200 text-red-800'
  if (c.s === 'On Leave') return 'bg-purple-200 text-purple-800'
  if (c.s === 'Work From Home') return 'bg-indigo-200 text-indigo-800'
  return 'bg-gray-100 text-gray-400'
}
function cellIcon(c) {
  if (!c.s) return '·'
  if (c.l) return '!'
  if (c.s === 'Present') return '✓'
  if (c.s === 'Half Day') return '½'
  if (c.s === 'Absent') return '✗'
  if (c.s === 'On Leave') return 'P'
  if (c.s === 'Work From Home') return 'W'
  return '?'
}
function isWeekend(d) {
  // calculate weekday from month + day
  const [m, y] = grid.value.month.split('/')
  const wd = new Date(Number(y), Number(m) - 1, Number(d)).getDay()
  return wd === 0 // Sunday
}

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }

let searchTimer = null
function debouncedSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(() => {}, 300) }

async function loadGrid() {
  gridLoading.value = true
  try {
    const [y, m] = period.value.split('-')
    grid.value = await frappeRequest({ url: 'hr.api.get_attendance_monthly_grid', method: 'GET', params: { year: y, month: m, department: filterDept.value || undefined } }) || grid.value
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải bảng công')) }
  gridLoading.value = false
}

async function exportGrid() {
  exporting.value = true
  try {
    const [y, m] = period.value.split('-')
    const res = await frappeRequest({ url: 'hr.api.export_attendance_csv', method: 'GET', params: { year: y, month: m, department: filterDept.value || undefined } })
    const blob = new Blob(['﻿' + (res.content || '')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = res.filename || 'bang_cong.csv'; a.click(); URL.revokeObjectURL(url)
    showToast('✅ Đã xuất ' + (res.count || 0) + ' NV')
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi xuất'), 4000) }
  exporting.value = false
}

onMounted(async () => {
  await Promise.all([
    loadGrid(),
    frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }).then(d => departments.value = d || []).catch(() => {}),
  ])
})
</script>
