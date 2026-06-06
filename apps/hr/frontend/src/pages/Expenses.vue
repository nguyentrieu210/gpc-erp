<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Chi phí</h1>
      <Button size="sm" @click="openForm"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo đề nghị</Button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-4xl mx-auto space-y-4">

        <!-- Dashboard -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-indigo-600">{{ dash.total ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Tổng đề nghị</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center cursor-pointer" @click="setFilter('Draft')">
            <div class="text-2xl font-bold text-amber-600">{{ dash.pending ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Chờ duyệt</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center cursor-pointer" @click="setFilter('Approved')">
            <div class="text-2xl font-bold text-green-600">{{ dash.approved ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Đã duyệt</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-lg font-bold text-emerald-600">{{ money(dash.this_month_amount) }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Chi tháng này</div>
          </div>
        </div>

        <!-- Tổng tiền chờ duyệt / đã duyệt -->
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-lg border border-amber-200 bg-amber-50/50 p-3 text-sm flex items-center justify-between">
            <span class="text-amber-700">⏳ Đang chờ duyệt</span>
            <span class="font-semibold text-amber-800">{{ money(dash.total_pending_amount) }}</span>
          </div>
          <div class="rounded-lg border border-green-200 bg-green-50/50 p-3 text-sm flex items-center justify-between">
            <span class="text-green-700">✅ Đã duyệt</span>
            <span class="font-semibold text-green-800">{{ money(dash.total_approved_amount) }}</span>
          </div>
        </div>

        <!-- List -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="text-sm font-semibold text-gray-700">📋 Danh sách đề nghị</h2>
            <select v-model="filterStatus" @change="loadList" class="text-xs border rounded-lg px-2 py-1">
              <option value="">Tất cả</option>
              <option value="Draft">Chờ duyệt</option>
              <option value="Approved">Đã duyệt</option>
              <option value="Rejected">Từ chối</option>
            </select>
          </div>
          <div v-if="loading" class="flex items-center justify-center py-12"><LoadingIndicator /></div>
          <div v-else-if="!list.length" class="text-center text-gray-400 py-12 text-sm">
            <FeatherIcon name="credit-card" class="mx-auto mb-2 h-8 w-8 text-gray-300" />
            Không có đề nghị nào
          </div>
          <div v-else class="divide-y">
            <div v-for="c in list" :key="c.name" class="flex items-center gap-3 px-4 py-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900 truncate cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + c.employee)">{{ c.employee_name }}</span>
                  <span class="text-xs text-gray-400">{{ c.name }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ $fmtDate(c.posting_date) }}</div>
              </div>
              <div class="text-right shrink-0">
                <div class="font-semibold text-gray-900">{{ money(c.total_claimed_amount) }}</div>
                <span class="text-[10px] px-2 py-0.5 rounded-full" :class="stateChip(c.state)">{{ c.state }}</span>
              </div>
              <div v-if="c.state === 'Chờ duyệt'" class="flex gap-1 shrink-0">
                <button @click="decide(c, true)" :disabled="busy[c.name]" class="p-1.5 rounded bg-green-100 text-green-700 hover:bg-green-200 disabled:opacity-50" title="Duyệt"><FeatherIcon name="check" class="h-4 w-4" /></button>
                <button @click="decide(c, false)" :disabled="busy[c.name]" class="p-1.5 rounded bg-red-100 text-red-700 hover:bg-red-200 disabled:opacity-50" title="Từ chối"><FeatherIcon name="x" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Tạo đề nghị -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showForm = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Đề nghị thanh toán / hoàn ứng</h2>
        <div class="space-y-3">
          <div><label class="text-xs text-gray-500">Nhân viên <span class="text-red-400">*</span></label>
            <select v-model="form.employee" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">— Chọn —</option><option v-for="e in employees" :key="e.name" :value="e.name">{{ e.employee_name }}</option></select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-500">Loại chi phí <span class="text-red-400">*</span></label>
              <select v-model="form.expense_type" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">—</option><option v-for="t in types" :key="t" :value="t">{{ vnType(t) }}</option></select>
            </div>
            <div><label class="text-xs text-gray-500">Ngày</label><input v-model="form.expense_date" type="date" class="w-full border rounded-lg px-3 py-2 text-sm" /></div>
          </div>
          <div><label class="text-xs text-gray-500">Số tiền (VNĐ) <span class="text-red-400">*</span></label><input v-model.number="form.amount" type="number" min="0" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="1500000" /></div>
          <div><label class="text-xs text-gray-500">Mô tả</label><textarea v-model="form.description" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Lý do chi..."></textarea></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showForm = false">Hủy</Button>
          <Button @click="submit" :loading="saving">Gửi đề nghị</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const dash = ref({})
const list = ref([])
const employees = ref([])
const types = ref([])
const loading = ref(false)
const toast = ref('')
const filterStatus = ref('')
const busy = reactive({})

const showForm = ref(false)
const saving = ref(false)
const form = reactive({ employee: '', expense_type: '', amount: '', description: '', expense_date: '' })

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }
function money(v) { return (Number(v) || 0).toLocaleString('vi-VN') + ' ₫' }
function vnType(t) { return { Travel: 'Công tác', Food: 'Ăn uống', Medical: 'Y tế', Calls: 'Điện thoại', Others: 'Khác' }[t] || t }
function stateChip(s) { return { 'Chờ duyệt': 'bg-amber-100 text-amber-700', 'Đã duyệt': 'bg-green-100 text-green-700', 'Từ chối': 'bg-red-100 text-red-700', 'Đã hủy': 'bg-gray-100 text-gray-500' }[s] || 'bg-gray-100' }

async function loadDash() {
  try { dash.value = await frappeRequest({ url: 'hr.api.get_expense_dashboard', method: 'GET', params: {} }) || {} } catch {}
}
async function loadList() {
  loading.value = true
  try { list.value = await frappeRequest({ url: 'hr.api.get_expense_claims', method: 'GET', params: { status: filterStatus.value || undefined } }) || [] } catch {}
  loading.value = false
}
function setFilter(s) { filterStatus.value = s; loadList() }

function openForm() {
  Object.assign(form, { employee: '', expense_type: '', amount: '', description: '', expense_date: new Date().toISOString().slice(0, 10) })
  showForm.value = true
}

async function submit() {
  if (!form.employee || !form.expense_type || !form.amount) { showToast('❌ Điền nhân viên, loại và số tiền'); return }
  saving.value = true
  try {
    await frappeRequest({ url: 'hr.api.create_expense_claim', method: 'POST', params: { ...form } })
    showForm.value = false
    showToast('✅ Đã gửi đề nghị')
    await Promise.all([loadDash(), loadList()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi'), 4000) }
  saving.value = false
}

async function decide(claim, approve) {
  busy[claim.name] = true
  try {
    await frappeRequest({ url: 'hr.api.approve_expense_claim', method: 'POST', params: { name: claim.name, approve: approve ? 1 : 0 } })
    showToast(approve ? '✅ Đã duyệt' : '✅ Đã từ chối')
    await Promise.all([loadDash(), loadList()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi'), 4000) }
  busy[claim.name] = false
}

onMounted(async () => {
  await Promise.all([
    loadDash(),
    loadList(),
    frappeRequest({ url: 'hr.api.get_employees', method: 'GET', params: { page_length: 200 } }).then(d => employees.value = d || []).catch(() => {}),
    frappeRequest({ url: 'hr.api.get_expense_claim_types', method: 'GET', params: {} }).then(d => types.value = d || []).catch(() => {}),
  ])
})
</script>
