<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Thuế & Phúc lợi</h1>
    </header>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-5xl mx-auto space-y-4">
        <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <template v-else>
          <p class="text-xs text-gray-400 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            ⚠️ Số liệu <b>ước tính</b> theo lương khoán/năm (ctc) của nhân viên. Bảo hiểm NV đóng 10.5% (BHXH 8% · BHYT 1.5% · BHTN 1%), công ty đóng 21.5%. Thuế TNCN lũy tiến (giảm trừ bản thân 11tr/tháng). Số liệu thực lấy từ Bảng lương khi có.
          </p>

          <!-- Dashboard -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-lg font-bold text-indigo-600">{{ money(dash.totals?.salary) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">Tổng lương/tháng</div>
            </div>
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-lg font-bold text-blue-600">{{ money(dash.totals?.ins_emp) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">BH nhân viên đóng</div>
            </div>
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-lg font-bold text-purple-600">{{ money(dash.totals?.ins_company) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">BH công ty đóng</div>
            </div>
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-lg font-bold text-red-600">{{ money(dash.totals?.tax) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">Thuế TNCN/tháng</div>
            </div>
          </div>

          <!-- Bảng chi tiết -->
          <div class="rounded-lg border bg-white shadow-sm overflow-hidden">
            <div class="px-4 py-3 border-b flex items-center justify-between">
              <h2 class="text-sm font-semibold text-gray-700">📋 Chi tiết theo nhân viên</h2>
              <label class="text-xs text-gray-500 flex items-center gap-1"><input type="checkbox" v-model="onlyWithSalary" /> Chỉ NV có lương</label>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm min-w-[680px]">
                <thead class="bg-gray-50 text-xs text-gray-500">
                  <tr>
                    <th class="text-left px-4 py-2 font-medium">Nhân viên</th>
                    <th class="text-right px-3 py-2 font-medium">Lương/tháng</th>
                    <th class="text-right px-3 py-2 font-medium">BHXH</th>
                    <th class="text-right px-3 py-2 font-medium">BHYT</th>
                    <th class="text-right px-3 py-2 font-medium">BHTN</th>
                    <th class="text-right px-3 py-2 font-medium">Thuế TNCN</th>
                    <th class="text-right px-4 py-2 font-medium">Thực lĩnh</th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  <tr v-for="r in visibleRows" :key="r.name" class="hover:bg-gray-50">
                    <td class="px-4 py-2">
                      <div class="font-medium text-gray-900 cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + r.name)">{{ r.employee_name }}</div>
                      <div class="text-xs text-gray-400">{{ r.designation || '—' }}</div>
                    </td>
                    <td class="text-right px-3 py-2 text-gray-700">{{ r.monthly ? short(r.monthly) : '—' }}</td>
                    <td class="text-right px-3 py-2 text-gray-500">{{ short(r.bhxh) }}</td>
                    <td class="text-right px-3 py-2 text-gray-500">{{ short(r.bhyt) }}</td>
                    <td class="text-right px-3 py-2 text-gray-500">{{ short(r.bhtn) }}</td>
                    <td class="text-right px-3 py-2 text-red-500">{{ short(r.tax) }}</td>
                    <td class="text-right px-4 py-2 font-semibold text-emerald-600">{{ r.monthly ? short(r.net) : '—' }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="!visibleRows.length" class="text-center text-gray-400 py-10 text-sm">Không có dữ liệu</div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const dash = ref({})
const loading = ref(true)
const onlyWithSalary = ref(false)

const visibleRows = computed(() => {
  const rows = dash.value.rows || []
  return onlyWithSalary.value ? rows.filter(r => r.has_salary) : rows
})

function money(v) { return (Number(v) || 0).toLocaleString('vi-VN') + ' ₫' }
function short(v) {
  const n = Number(v) || 0
  if (n >= 1e9) return (n / 1e9).toFixed(1) + ' tỷ'
  if (n >= 1e6) return (n / 1e6).toFixed(1) + ' tr'
  if (n >= 1e3) return Math.round(n / 1e3) + 'k'
  return n.toString()
}

onMounted(async () => {
  try { dash.value = await frappeRequest({ url: 'hr.api.get_benefits_dashboard', method: 'GET', params: {} }) || {} } catch {}
  loading.value = false
})
</script>
