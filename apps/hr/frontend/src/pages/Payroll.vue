<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Bảng lương</h1>
      <input type="month" v-model="period" @change="loadSlips" class="text-sm border rounded-lg px-2 py-1.5" />
      <Button v-if="periodStatus.locked" size="sm" theme="red" variant="subtle" @click="toggleLock(false)">🔒 Đã khóa</Button>
      <Button v-else size="sm" @click="openConfirm" :disabled="periodStatus.locked"><FeatherIcon name="play" class="h-4 w-4" /> Chạy lương</Button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium max-w-sm"
      :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-4xl mx-auto space-y-4">

        <!-- Summary -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-sm font-bold text-gray-900">{{ money(summary.gross) }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Tổng lương (gross)</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-sm font-bold text-red-600">{{ money(summary.deduct) }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Tổng khấu trừ</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-sm font-bold text-green-600">{{ money(summary.net) }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Thực lãnh</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-sm font-bold text-gray-900">{{ summary.count }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Phiếu lương · {{ periodLabel }}</div>
          </div>
        </div>

        <!-- Kết quả chạy lương gần nhất -->
        <div v-if="runResult" class="rounded-lg border border-indigo-200 bg-indigo-50/60 p-3 text-sm">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-indigo-800">Kết quả chạy lương kỳ {{ runResult.period }}</span>
            <button @click="runResult = null" class="text-indigo-400 hover:text-indigo-600"><FeatherIcon name="x" class="h-4 w-4" /></button>
          </div>
          <div class="mt-1 text-indigo-700">
            ✅ Tạo mới <b>{{ runResult.created.length }}</b> · ⏭️ Bỏ qua <b>{{ runResult.skipped.length }}</b>
            <span v-if="runResult.errors.length" class="text-red-600"> · ❌ Lỗi <b>{{ runResult.errors.length }}</b></span>
          </div>
          <ul v-if="runResult.skipped.length" class="mt-1 text-xs text-indigo-600/80 list-disc pl-5">
            <li v-for="s in runResult.skipped" :key="s.employee">{{ s.name }} — {{ s.reason }}</li>
          </ul>
          <ul v-if="runResult.errors.length" class="mt-1 text-xs text-red-600 list-disc pl-5">
            <li v-for="e in runResult.errors" :key="e.employee">{{ e.name }} — {{ e.error }}</li>
          </ul>
        </div>

        <!-- Search + list -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="px-4 py-3 border-b flex items-center gap-2">
            <h2 class="text-sm font-semibold text-gray-700 flex-1">📋 Phiếu lương {{ periodLabel }}
              <span v-if="periodStatus.locked" class="text-[10px] text-red-500 font-normal ml-1">(Đã khóa)</span>
            </h2>
            <div class="flex items-center gap-2">
              <Button v-if="periodStatus.draft > 0 && !periodStatus.locked" size="sm" variant="subtle" @click="submitAll" :loading="submitingAll"><FeatherIcon name="check-circle" class="h-3.5 w-3.5" /> Chốt tất cả {{ periodStatus.draft }}</Button>
              <Button v-if="periodStatus.submitted > 0" size="sm" variant="subtle" @click="toggleLock(!periodStatus.locked)">{{ periodStatus.locked ? '🔓 Mở khóa' : '🔒 Khóa kỳ' }}</Button>
              <input v-model="search" placeholder="🔍 Tên nhân viên..." class="text-sm border rounded-lg px-3 py-1.5 max-w-[200px]" />
            </div>
          </div>

          <div v-if="loading" class="flex items-center justify-center py-12"><LoadingIndicator /></div>
          <div v-else-if="!filteredSlips.length" class="text-center text-gray-400 py-12 text-sm">
            <FeatherIcon name="file-text" class="mx-auto mb-2 h-8 w-8 text-gray-300" />
            Chưa có phiếu lương cho kỳ {{ periodLabel }}.
            <div class="mt-1 text-xs">Bấm <b>Chạy lương</b> để tạo phiếu cho nhân viên có lương khoán.</div>
          </div>

          <div v-else class="divide-y">
            <div v-for="s in filteredSlips" :key="s.name">
              <div class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer" @click="toggleDetail(s)">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900 truncate">{{ s.employee_name }}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded-full" :class="statusChip(s.docstatus)">{{ statusLabel(s.docstatus) }}</span>
                  </div>
                  <div class="text-xs text-gray-500">{{ $fmtDate(s.start_date) }} → {{ $fmtDate(s.end_date) }} · {{ s.designation || '—' }}</div>
                </div>
                <div class="text-right shrink-0">
                  <div class="text-sm font-semibold text-green-700">{{ money(s.net_pay) }}</div>
                  <div class="text-xs text-gray-400">khấu trừ {{ money(s.total_deduction) }}</div>
                </div>
                <FeatherIcon name="chevron-down" class="h-4 w-4 text-gray-400 ml-2 transition-transform" :class="expanded === s.name ? 'rotate-180' : ''" />
              </div>

              <!-- Expand: breakdown -->
              <div v-if="expanded === s.name" class="bg-gray-50/70 px-4 py-3 border-t">
                <div v-if="detailLoading" class="text-xs text-gray-400 py-2 text-center"><LoadingIndicator class="inline h-4 w-4" /> Đang tải...</div>
                <div v-else-if="detail[s.name]" class="grid sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div class="text-xs font-semibold text-gray-500 uppercase mb-1">Thu nhập</div>
                    <div v-for="r in detail[s.name].earnings" :key="r.component" class="flex justify-between py-0.5">
                      <span class="text-gray-600">{{ r.component }}</span><span class="font-medium text-gray-800">{{ money(r.amount) }}</span>
                    </div>
                    <div class="flex justify-between py-1 mt-1 border-t font-semibold">
                      <span>Tổng thu nhập</span><span>{{ money(detail[s.name].gross_pay) }}</span>
                    </div>
                  </div>
                  <div>
                    <div class="text-xs font-semibold text-gray-500 uppercase mb-1">Khấu trừ</div>
                    <div v-for="r in detail[s.name].deductions" :key="r.component" class="flex justify-between py-0.5">
                      <span class="text-gray-600">{{ r.component }}</span><span class="font-medium text-red-600">-{{ money(r.amount) }}</span>
                    </div>
                    <div v-if="!detail[s.name].deductions.length" class="text-gray-400 py-0.5">Không có khấu trừ</div>
                    <div class="flex justify-between py-1 mt-1 border-t font-semibold">
                      <span>Tổng khấu trừ</span><span class="text-red-600">-{{ money(detail[s.name].total_deduction) }}</span>
                    </div>
                  </div>
                  <div class="sm:col-span-2 flex items-center justify-between pt-2 border-t">
                    <span class="font-semibold text-gray-700">💰 Thực lãnh</span>
                    <span class="text-base font-bold text-green-700">{{ money(detail[s.name].net_pay) }}</span>
                  </div>
                  <div class="sm:col-span-2 flex justify-end gap-2">
                    <Button size="sm" variant="subtle" @click.stop="printSlip(s)"><FeatherIcon name="printer" class="h-3.5 w-3.5" /> In phiếu</Button>
                    <Button v-if="s.docstatus === 0" size="sm" variant="subtle" @click.stop="finalize(s)" :loading="busy[s.name]"><FeatherIcon name="check" class="h-3.5 w-3.5" /> Chốt</Button>
                    <Button v-if="s.docstatus === 0" size="sm" theme="red" variant="subtle" @click.stop="remove(s)" :loading="busy[s.name]"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /> Xóa</Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: xác nhận chạy lương -->
    <div v-if="showConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showConfirm = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6">
        <h2 class="text-lg font-semibold mb-2">Chạy bảng lương kỳ {{ periodLabel }}</h2>
        <p class="text-sm text-gray-600 mb-1">Ngày công chuẩn: <b>{{ wdInfo.total_working_days }}</b> ngày (trừ CN + lễ). Để trống = full tháng.</p>
        <p class="text-xs text-gray-400 mb-3">BHXH/BHYT/BHTN tính trên mức lương hợp đồng (không prorate). Lương/phụ cấp/thuế TNCN prorate theo ngày công thực.</p>
        <div class="border rounded-lg divide-y max-h-60 overflow-y-auto">
          <div class="flex items-center gap-3 px-3 py-2 bg-gray-50 text-xs text-gray-500 font-semibold">
            <span class="flex-1">Nhân viên</span>
            <span class="w-16 text-right">Lương CB</span>
            <span class="w-20 text-center">Ngày công</span>
          </div>
          <div v-for="e in wdInfo.employees" :key="e.name" class="flex items-center gap-3 px-3 py-2 text-sm" :class="{ 'bg-indigo-50/50': wdDays[e.name] }">
            <span class="flex-1 truncate">{{ e.employee_name }}</span>
            <span class="w-16 text-right text-xs text-gray-500">{{ e.luong_co_ban ? money(e.luong_co_ban) : '—' }}</span>
            <input v-model.number="wdDays[e.name]" type="number" :min="0" :max="wdInfo.total_working_days" :placeholder="wdInfo.total_working_days" class="w-20 text-center border rounded-lg px-2 py-1.5 text-sm" />
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-3">NV có lương nhưng bỏ trống = đi đủ công. NV đã có phiếu kỳ này sẽ được bỏ qua.</p>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showConfirm = false">Hủy</Button>
          <Button theme="green" @click="runPayroll" :loading="running">Chạy lương</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const period = ref(new Date().toISOString().slice(0, 7)) // "YYYY-MM"
const slips = ref([])
const loading = ref(false)
const running = ref(false)
const submitingAll = ref(false)
const toast = ref('')
const search = ref('')
const showConfirm = ref(false)
const wdInfo = ref({ total_working_days: 26, employees: [] })
const wdDays = reactive({})
const runResult = ref(null)
const periodStatus = ref({ draft: 0, submitted: 0, locked: false })
const expanded = ref(null)
const detail = reactive({})
const detailLoading = ref(false)
const busy = reactive({})

const ym = computed(() => { const [y, m] = period.value.split('-'); return { year: Number(y), month: Number(m) } })
const periodLabel = computed(() => { const { year, month } = ym.value; return `${String(month).padStart(2, '0')}/${year}` })

const filteredSlips = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return slips.value
  return slips.value.filter(s => (s.employee_name || '').toLowerCase().includes(q))
})

const summary = computed(() => {
  const s = slips.value || []
  return {
    count: s.length,
    gross: s.reduce((t, x) => t + (x.gross_pay || 0), 0),
    deduct: s.reduce((t, x) => t + (x.total_deduction || 0), 0),
    net: s.reduce((t, x) => t + (x.net_pay || 0), 0),
  }
})

function money(v) { return (Number(v) || 0).toLocaleString('vi-VN') + ' ₫' }
function showToast(msg, ms = 4000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }
function statusLabel(d) { return { 0: 'Nháp', 1: 'Đã chốt', 2: 'Đã hủy' }[d] || '—' }
function statusChip(d) { return { 0: 'bg-amber-100 text-amber-700', 1: 'bg-green-100 text-green-700', 2: 'bg-gray-100 text-gray-500' }[d] || 'bg-gray-100' }

async function toggleDetail(s) {
  if (expanded.value === s.name) { expanded.value = null; return }
  expanded.value = s.name
  if (detail[s.name]) return
  detailLoading.value = true
  try {
    detail[s.name] = await frappeRequest({ url: 'hr.api.get_salary_slip_detail', method: 'GET', params: { name: s.name } })
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải chi tiết')) }
  detailLoading.value = false
}

async function openConfirm() {
  showConfirm.value = true
  try {
    const { year, month } = ym.value
    wdInfo.value = await frappeRequest({ url: 'hr.api.get_working_days_info', method: 'GET', params: { year, month } }) || wdInfo.value
    wdInfo.value.employees.forEach(e => { if (!(e.name in wdDays)) wdDays[e.name] = wdInfo.value.total_working_days })
  } catch {}
}

async function runPayroll() {
  running.value = true
  try {
    const { year, month } = ym.value
    const days = {}
    wdInfo.value.employees.forEach(e => { if (wdDays[e.name] && wdDays[e.name] !== wdInfo.value.total_working_days) days[e.name] = wdDays[e.name] })
    const res = await frappeRequest({ url: 'hr.api.run_payroll', method: 'POST', params: { year, month, working_days: Object.keys(days).length ? JSON.stringify(days) : undefined } })
    runResult.value = res
    showConfirm.value = false
    showToast(`✅ Đã tạo ${res.created.length} phiếu · bỏ qua ${res.skipped.length}`)
    await loadSlips()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi chạy lương')) }
  running.value = false
}

async function finalize(s) {
  busy[s.name] = true
  try {
    await frappeRequest({ url: 'hr.api.submit_salary_slip', method: 'POST', params: { name: s.name } })
    showToast('✅ Đã chốt lương')
    await loadSlips()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi chốt lương')) }
  busy[s.name] = false
}

async function remove(s) {
  busy[s.name] = true
  try {
    await frappeRequest({ url: 'hr.api.delete_salary_slip', method: 'POST', params: { name: s.name } })
    delete detail[s.name]
    showToast('✅ Đã xóa phiếu lương')
    await loadSlips()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi xóa')) }
  busy[s.name] = false
}

async function loadPeriodStatus() {
  try {
    const { year, month } = ym.value
    periodStatus.value = await frappeRequest({ url: 'hr.api.get_payroll_period_status', method: 'GET', params: { year, month } }) || periodStatus.value
  } catch {}
}

async function submitAll() {
  if (!confirm('Chốt toàn bộ phiếu lương Nháp kỳ ' + periodLabel.value + '?')) return
  submitingAll.value = true
  try {
    const { year, month } = ym.value
    const r = await frappeRequest({ url: 'hr.api.submit_all_salary_slips', method: 'POST', params: { year, month } })
    showToast(`✅ Đã chốt ${r.submitted} phiếu` + (r.errors.length ? ` · ${r.errors.length} lỗi` : ''))
    await loadSlips(); await loadPeriodStatus()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi chốt')) }
  submitingAll.value = false
}

async function toggleLock(lock) {
  try {
    const { year, month } = ym.value
    await frappeRequest({ url: 'hr.api.lock_payroll_period', method: 'POST', params: { year, month, unlock: lock ? 0 : 1 } })
    periodStatus.value.locked = lock !== false
    showToast(lock !== false ? '✅ Đã khóa kỳ ' + periodLabel.value : '✅ Đã mở khóa')
    await loadPeriodStatus()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi')) }
}

async function printSlip(s) {
  try {
    const res = await frappeRequest({ url: 'hr.api.print_salary_slip', method: 'GET', params: { name: s.name } })
    const w = window.open('', '_blank'); if (w) { w.document.write(res.html); w.document.close() }
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi in phiếu')) }
}

async function loadSlips() {
  loading.value = true; expanded.value = null
  try {
    const { year, month } = ym.value
    slips.value = await frappeRequest({ url: 'hr.api.get_salary_slips', method: 'GET', params: { year, month } }) || []
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải bảng lương')) }
  loading.value = false
  await loadPeriodStatus()
}

onMounted(loadSlips)
</script>
