<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Nghỉ phép</h1>
      <Button size="sm" variant="subtle" @click="autoAllocate" :loading="allocating"><FeatherIcon name="refresh-cw" class="h-4 w-4" /> Cấp phép toàn CT</Button>
      <Button size="sm" @click="openForm"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo đơn</Button>
    </header>
    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>
    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-5xl mx-auto space-y-4">

        <!-- Quick stats -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-indigo-600">{{ dash.total ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Tổng đơn</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center cursor-pointer" @click="showLeaveList = !showLeaveList; setFilter('Open')"><div class="text-2xl font-bold text-amber-600">{{ dash.pending ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Chờ duyệt</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center cursor-pointer" @click="showLeaveList = !showLeaveList; setFilter('Approved')"><div class="text-2xl font-bold text-green-600">{{ dash.approved ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Đã duyệt</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-cyan-600">{{ dash.days_approved ?? '—' }}</div><div class="text-xs text-gray-500 mt-0.5">Ngày ĐD</div></div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center"><div class="text-2xl font-bold text-gray-600">{{ balTotal }}</div><div class="text-xs text-gray-500 mt-0.5">Nhân viên</div></div>
        </div>

        <!-- Bảng số dư phép toàn NV -->
        <div class="rounded-lg border bg-white shadow-sm overflow-hidden">
          <div class="px-4 py-3 border-b flex items-center gap-2 flex-wrap">
            <h2 class="text-sm font-semibold text-gray-700 flex-1">📊 Số dư ngày phép</h2>
            <input v-model="filter.search" @input="debouncedSearch" placeholder="🔍 Tìm NV..." class="text-sm border rounded-lg px-2 py-1.5 max-w-[180px]" />
            <select v-model="filter.department" @change="reload" class="text-sm border rounded-lg px-2 py-1.5">
              <option value="">Tất cả phòng ban</option><option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
            </select>
            <span class="text-xs text-gray-400">Tổng <b class="text-gray-700">{{ totalBal }}</b> NV</span>
          </div>
          <div v-if="balLoading" class="flex items-center justify-center py-12"><LoadingIndicator /></div>
          <div v-else-if="!balData.length" class="text-center text-gray-400 py-12 text-sm">Không có dữ liệu</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50/70 text-[11px] font-semibold text-gray-400 uppercase">
                <tr>
                  <th class="text-left px-4 py-2 sticky left-0 bg-gray-50/70">Nhân viên</th>
                  <th class="hidden md:table-cell text-left px-3 py-2">Phòng ban</th>
                  <th v-for="lt in balLeaveTypes" :key="lt" class="text-center px-3 py-2">{{ lt }}</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                <tr v-for="r in balData" :key="r.name" class="hover:bg-gray-50 cursor-pointer" @click="$router.push('/employees/' + r.name)">
                  <td class="px-4 py-2.5 sticky left-0 bg-white">
                    <span class="font-medium text-gray-900">{{ r.employee_name }}</span>
                    <div class="text-xs text-gray-400 sm:hidden">{{ r.department || '—' }}</div>
                  </td>
                  <td class="hidden md:table-cell px-3 py-2.5 text-xs text-gray-500">{{ r.department || '—' }}</td>
                  <td v-for="lt in balLeaveTypes" :key="lt" class="text-center px-3 py-2.5">
                    <div class="flex items-center gap-1 justify-center">
                      <span class="font-semibold" :class="(r['bal_' + lt] || 0) <= 0 ? 'text-red-500' : (r['bal_' + lt] || 0) <= 2 ? 'text-amber-600' : 'text-indigo-600'">{{ r['bal_' + lt] ?? '—' }}</span>
                      <span class="text-[10px] text-gray-400">/{{ r['alloc_' + lt] || 0 }}</span>
                    </div>
                    <div class="w-full h-1.5 bg-gray-100 rounded-full mt-0.5 max-w-[60px] mx-auto">
                      <div class="h-full rounded-full" :class="(r['bal_' + lt] || 0) <= 0 ? 'bg-red-400' : (r['bal_' + lt] || 0) <= 2 ? 'bg-amber-400' : 'bg-indigo-400'"
                        :style="{ width: Math.max(3, Math.min(100, ((r['used_' + lt] || 0) / Math.max(1, r['alloc_' + lt] || 1)) * 100)) + '%' }"></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- Pagination -->
            <div v-if="balPages > 1" class="flex items-center justify-center gap-1 py-3 border-t text-sm">
              <button @click="goPage(balPage - 1)" :disabled="balPage <= 1" class="px-2 py-1 rounded border bg-white disabled:opacity-40">‹</button>
              <button v-for="p in pageList" :key="p" @click="typeof p === 'number' && goPage(p)" :disabled="p==='…'" class="min-w-[30px] px-2 py-1 rounded border" :class="p===balPage?'bg-indigo-600 text-white border-indigo-600':(p==='…'?'border-transparent':'bg-white')">{{ p }}</button>
              <button @click="goPage(balPage + 1)" :disabled="balPage >= balPages" class="px-2 py-1 rounded border bg-white disabled:opacity-40">›</button>
            </div>
          </div>
        </div>

        <!-- Đơn nghỉ phép -->
        <div class="rounded-lg border bg-white shadow-sm overflow-hidden" v-if="showLeaveList">
          <div class="px-4 py-3 border-b flex items-center gap-3">
            <h2 class="text-sm font-semibold text-gray-700 flex-1">📋 Đơn nghỉ phép</h2>
            <input v-model="filterMonth" @change="loadList" type="month" class="text-xs border rounded-lg px-2 py-1" />
            <select v-model="filterStatus" @change="loadList" class="text-xs border rounded-lg px-2 py-1"><option value="">Tất cả</option><option value="Open">Chờ duyệt</option><option value="Approved">Đã duyệt</option><option value="Rejected">Từ chối</option></select>
          </div>
          <div v-if="loading" class="flex items-center justify-center py-12"><LoadingIndicator /></div>
          <div v-else-if="!list.length" class="text-center text-gray-400 py-12 text-sm">Không có đơn nào</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-50/70 text-[11px] font-semibold text-gray-400 uppercase">
                <tr><th class="text-left px-4 py-2">Nhân viên</th><th class="text-left px-3 py-2 hidden sm:table-cell">Loại</th><th class="text-left px-3 py-2 hidden md:table-cell">Từ→Đến</th><th class="text-center px-3 py-2">Ngày</th><th class="text-center px-3 py-2">TT</th><th class="text-right px-4 py-2">Thao tác</th></tr>
              </thead>
              <tbody class="divide-y">
                <tr v-for="l in list" :key="l.name" class="hover:bg-gray-50">
                  <td class="px-4 py-2.5"><span class="font-medium text-gray-900 cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + l.employee)">{{ l.employee_name }}</span></td>
                  <td class="px-3 py-2.5 hidden sm:table-cell"><span class="text-xs px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700">{{ l.leave_type }}</span></td>
                  <td class="px-3 py-2.5 text-xs text-gray-500 hidden md:table-cell">{{ $fmtDate(l.from_date) }} → {{ $fmtDate(l.to_date) }}</td>
                  <td class="px-3 py-2.5 text-center font-medium">{{ l.total_leave_days || 0 }}</td>
                  <td class="px-3 py-2.5 text-center"><span class="text-[10px] px-2 py-0.5 rounded-full" :class="statusChip(l.status)">{{ statusLabel(l.status) }}</span></td>
                  <td class="px-4 py-2.5 text-right">
                    <div v-if="l.status === 'Open'" class="flex gap-1 justify-end">
                      <button @click="decide(l, true)" :disabled="busy[l.name]" class="px-2 py-1 rounded text-xs bg-green-100 text-green-700 hover:bg-green-200 disabled:opacity-50" title="Duyệt">✓</button>
                      <button @click="decide(l, false)" :disabled="busy[l.name]" class="px-2 py-1 rounded text-xs bg-red-100 text-red-700 hover:bg-red-200 disabled:opacity-50" title="Từ chối">✗</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal tạo đơn -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showForm = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Tạo đơn nghỉ phép</h2>
        <div class="space-y-3">
          <div><label class="text-xs text-gray-500">Nhân viên <span class="text-red-400">*</span></label><select v-model="form.employee" @change="onEmpSelect" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">— Chọn —</option><option v-for="e in employees" :key="e.name" :value="e.name">{{ e.employee_name }}</option></select></div>
          <div><label class="text-xs text-gray-500">Loại nghỉ <span class="text-red-400">*</span></label><select v-model="form.leave_type" @change="onTypeSelect" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="t in leaveTypes" :key="t" :value="t">{{ t }}</option></select></div>
          <div v-if="formRemaining !== null" class="text-xs rounded-lg p-2" :class="formRemaining >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">Số ngày còn: <b>{{ Math.max(0, formRemaining || 0) }}</b> ngày</div>
          <div class="grid grid-cols-2 gap-3"><div><label class="text-xs text-gray-500">Từ <span class="text-red-400">*</span></label><input v-model="form.from_date" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div><div><label class="text-xs text-gray-500">Đến <span class="text-red-400">*</span></label><input v-model="form.to_date" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div></div>
          <div><label class="text-xs text-gray-500">Lý do</label><textarea v-model="form.reason" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Lý do nghỉ..."></textarea></div>
        </div>
        <div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="showForm = false">Hủy</Button><Button @click="submit" :loading="saving">Gửi đơn</Button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const dash = ref({}); const list = ref([]); const employees = ref([]); const leaveTypes = ref([]); const departments = ref([])
const loading = ref(false); const toast = ref(''); const filterStatus = ref(''); const filterMonth = ref('')
const busy = reactive({}); const showForm = ref(false); const saving = ref(false)
const form = reactive({ employee: '', leave_type: '', from_date: '', to_date: '', reason: '' })
const formRemaining = ref(null); const funding = ref(false)
const showLeaveList = ref(false)
const filter = reactive({ search: '', department: '' })
const balData = ref([]); const balLeaveTypes = ref([]); const balLoading = ref(false)
const totalBal = ref(0); const balPage = ref(1); const balPages = ref(1)

const balTotal = computed(() => balData.value.length ? totalBal.value : '—')

const pageList = computed(() => {
  const p = balPage.value, n = balPages.value, out = []
  if (n <= 7) { for (let i = 1; i <= n; i++) out.push(i); return out }
  out.push(1); if (p > 3) out.push('…')
  for (let i = Math.max(2, p - 1); i <= Math.min(n - 1, p + 1); i++) out.push(i)
  if (p < n - 2) out.push('…'); out.push(n); return out
})

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }
function statusLabel(s) { return { Open: 'Chờ duyệt', Approved: 'Đã duyệt', Rejected: 'Từ chối', Cancelled: 'Đã hủy' }[s] || s }
function statusChip(s) { return { Open: 'bg-amber-100 text-amber-700', Approved: 'bg-green-100 text-green-700', Rejected: 'bg-red-100 text-red-700', Cancelled: 'bg-gray-100 text-gray-500' }[s] || 'bg-gray-100' }

let searchTimer = null
function debouncedSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(reload, 350) }

async function loadBalTable() {
  balLoading.value = true
  try {
    const res = await frappeRequest({ url: 'hr.api.get_all_leave_balances', method: 'GET', params: { ...filter, page: balPage.value, page_length: 30 } })
    balData.value = res.data || []
    balLeaveTypes.value = res.leave_types || []
    totalBal.value = res.total || 0
    balPages.value = res.pages || 1
  } catch {}
  balLoading.value = false
}
function reload() { balPage.value = 1; loadBalTable() }
function goPage(n) { if (n >= 1 && n <= balPages.value && n !== balPage.value) { balPage.value = n; loadBalTable() } }

async function loadDash() { try { dash.value = await frappeRequest({ url: 'hr.api.get_leave_dashboard', method: 'GET', params: {} }) || {} } catch {} }
async function loadList() {
  loading.value = true
  try { const p = { status: filterStatus.value || undefined }; if (filterMonth.value) p.month = filterMonth.value; list.value = await frappeRequest({ url: 'hr.api.get_leave_applications', method: 'GET', params: p }) || [] } catch {}
  loading.value = false
}
function setFilter(s) { filterStatus.value = s; loadList() }

async function autoAllocate() {
  funding.value = true
  try { const r = await frappeRequest({ url: 'hr.api.auto_allocate_all', method: 'POST', params: {} }); showToast('✅ Đã cấp cho ' + r.count + ' NV'); await loadBalTable() } catch (e) { showToast('❌ ' + (e.message || 'Lỗi')) }
  funding.value = false
}

function onEmpSelect() { if (form.employee && form.leave_type) checkFormBalance() }
function onTypeSelect() { if (form.employee && form.leave_type) checkFormBalance(); else formRemaining.value = null }
async function checkFormBalance() {
  try { const b = await frappeRequest({ url: 'hr.api.get_leave_balance', method: 'GET', params: { employee: form.employee } }); formRemaining.value = (b || []).find(x => x.leave_type === form.leave_type)?.remaining ?? null } catch {}
}
function openForm() { Object.assign(form, { employee: '', leave_type: '', from_date: '', to_date: '', reason: '' }); formRemaining.value = null; showForm.value = true }
async function submit() {
  if (!form.employee || !form.leave_type || !form.from_date || !form.to_date) { showToast('❌ Điền đủ thông tin'); return }
  saving.value = true
  try { await frappeRequest({ url: 'hr.api.create_leave_application', method: 'POST', params: { ...form } }); showForm.value = false; showToast('✅ Đã gửi đơn nghỉ'); await Promise.all([loadDash(), loadList(), loadBalTable()]) } catch (e) { showToast('❌ ' + (e.message || 'Lỗi')) }
  saving.value = false
}
async function decide(l, approve) {
  busy[l.name] = true
  try { await frappeRequest({ url: 'hr.api.approve_leave', method: 'POST', params: { name: l.name, approve: approve ? 1 : 0 } }); showToast(approve ? '✅ Đã duyệt' : '✅ Đã từ chối'); await Promise.all([loadDash(), loadList(), loadBalTable()]) } catch (e) { showToast('❌ ' + (e.message || 'Lỗi')) }
  busy[l.name] = false
}

onMounted(async () => {
  await Promise.all([
    loadDash(), loadList(), loadBalTable(),
    frappeRequest({ url: 'hr.api.get_employees', method: 'GET', params: { page_length: 200 } }).then(d => employees.value = d || []).catch(() => {}),
    frappeRequest({ url: 'hr.api.get_leave_types', method: 'GET', params: {} }).then(d => leaveTypes.value = d || []).catch(() => {}),
    frappeRequest({ url: 'hr.api.get_departments', method: 'GET', params: {} }).then(d => departments.value = d || []).catch(() => {}),
  ])
})
</script>
