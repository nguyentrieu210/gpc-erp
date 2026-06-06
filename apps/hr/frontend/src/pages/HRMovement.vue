<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Biến động nhân sự</h1>
      <select v-model.number="year" @change="load" class="text-sm border rounded-lg px-2 py-1.5">
        <option v-for="y in years" :key="y" :value="y">Năm {{ y }}</option>
      </select>
    </header>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else class="max-w-4xl mx-auto space-y-4">
        <!-- Stat cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-indigo-600">{{ d.active }}</div><div class="text-xs text-gray-500 mt-0.5">Đang làm việc</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-green-600">+{{ d.joined }}</div><div class="text-xs text-gray-500 mt-0.5">Tuyển mới ({{ year }})</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-red-500">−{{ d.left }}</div><div class="text-xs text-gray-500 mt-0.5">Nghỉ việc ({{ year }})</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-amber-600">{{ d.turnover }}%</div><div class="text-xs text-gray-500 mt-0.5">Tỷ lệ nghỉ việc</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-lg border border-green-200 bg-green-50/50 p-3 text-sm flex items-center justify-between"><span class="text-green-700">📈 Thăng chức/bổ nhiệm</span><span class="font-semibold text-green-800">{{ d.promotions }}</span></div>
          <div class="rounded-lg border border-blue-200 bg-blue-50/50 p-3 text-sm flex items-center justify-between"><span class="text-blue-700">🔀 Điều chuyển</span><span class="font-semibold text-blue-800">{{ d.transfers }}</span></div>
        </div>

        <!-- Biểu đồ vào/ra theo tháng -->
        <div class="rounded-lg border bg-white shadow-sm p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Vào / Ra theo tháng</h3>
          <div class="flex items-end gap-1 h-40">
            <div v-for="m in d.months" :key="m.m" class="flex-1 flex flex-col items-center justify-end gap-0.5 h-full">
              <div class="w-full flex flex-col justify-end items-center gap-0.5 flex-1">
                <div class="w-3 bg-green-500 rounded-t" :style="{ height: barH(m.join) + 'px' }" :title="'Vào: ' + m.join"></div>
                <div class="w-3 bg-red-400 rounded-t" :style="{ height: barH(m.leave) + 'px' }" :title="'Ra: ' + m.leave"></div>
              </div>
              <span class="text-[10px] text-gray-400">{{ m.label }}</span>
            </div>
          </div>
          <div class="flex gap-4 justify-center mt-2 text-xs text-gray-500">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 bg-green-500 rounded-sm"></span> Vào làm</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 bg-red-400 rounded-sm"></span> Nghỉ việc</span>
          </div>
        </div>

        <!-- Phân bổ thâm niên -->
        <div class="rounded-lg border bg-white shadow-sm p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Phân bổ thâm niên</h3>
          <div class="space-y-2">
            <div v-for="(c, k) in d.tenure" :key="k" class="flex items-center gap-2 text-sm">
              <span class="w-20 text-gray-600">{{ k }}</span>
              <div class="flex-1 h-4 rounded-full bg-gray-100 overflow-hidden">
                <div class="h-full rounded-full bg-indigo-500" :style="{ width: tenurePct(c) + '%' }"></div>
              </div>
              <span class="w-8 text-right text-gray-500">{{ c }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const now = new Date().getFullYear()
const years = [now + 1, now, now - 1, now - 2]
const year = ref(now)
const d = ref({ months: [], tenure: {}, active: 0, joined: 0, left: 0, turnover: 0, promotions: 0, transfers: 0 })
const loading = ref(true)

const maxMonth = computed(() => Math.max(1, ...((d.value.months || []).flatMap(m => [m.join, m.leave]))))
const maxTenure = computed(() => Math.max(1, ...Object.values(d.value.tenure || {})))
function barH(v) { return Math.round((v / maxMonth.value) * 60) }
function tenurePct(v) { return Math.round((v / maxTenure.value) * 100) }

async function load() {
  loading.value = true
  try { d.value = await frappeRequest({ url: 'hr.api.get_hr_movement_dashboard', method: 'GET', params: { year: year.value } }) || d.value } catch {}
  loading.value = false
}
load()
</script>
