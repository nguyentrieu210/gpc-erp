<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Hiệu suất & KPI</h1>
      <Button size="sm" variant="subtle" @click="openCycle"><FeatherIcon name="refresh-cw" class="h-4 w-4" /> Tạo chu kỳ</Button>
      <Button size="sm" @click="openForm"><FeatherIcon name="plus" class="h-4 w-4" /> Đánh giá mới</Button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-4xl mx-auto space-y-4">

        <!-- Dashboard -->
        <div class="grid grid-cols-3 gap-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-indigo-600">{{ dash.total ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Tổng đánh giá</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-emerald-600">{{ dash.avg_score ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Điểm trung bình</div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
            <div class="text-2xl font-bold text-amber-600">{{ dash.this_month ?? '—' }}</div>
            <div class="text-xs text-gray-500 mt-0.5">Đánh giá tháng này</div>
          </div>
        </div>

        <!-- Phân bố xếp loại + Top performers -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="rounded-lg border bg-white shadow-sm p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">📊 Phân bố xếp loại</h3>
            <div v-if="!hasBands" class="text-center text-gray-400 py-6 text-sm">Chưa có dữ liệu</div>
            <div v-else class="space-y-2">
              <div v-for="b in bands" :key="b.key" class="flex items-center gap-2 text-sm">
                <span class="w-24 text-gray-600">{{ b.key }}</span>
                <div class="flex-1 h-4 rounded-full bg-gray-100 overflow-hidden">
                  <div class="h-full rounded-full transition-all" :class="b.color" :style="{ width: bandPct(b.count) + '%' }"></div>
                </div>
                <span class="w-6 text-right text-xs font-medium text-gray-700">{{ b.count }}</span>
              </div>
            </div>
          </div>

          <div class="rounded-lg border bg-white shadow-sm p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">🏆 Top hiệu suất</h3>
            <div v-if="!dash.top?.length" class="text-center text-gray-400 py-6 text-sm">Chưa có dữ liệu</div>
            <div v-else class="space-y-2">
              <div v-for="(t, i) in dash.top" :key="t.employee" class="flex items-center gap-3 text-sm">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" :class="['bg-amber-100 text-amber-700','bg-gray-100 text-gray-600','bg-orange-100 text-orange-700','bg-gray-50 text-gray-500','bg-gray-50 text-gray-500'][i]">{{ i + 1 }}</div>
                <span class="flex-1 font-medium text-gray-800 truncate cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + t.employee)">{{ t.employee_name }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="bandChip(t.band)">{{ t.score }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Danh sách đánh giá -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="text-sm font-semibold text-gray-700">📋 Đánh giá gần đây</h2>
            <select v-model="filterEmployee" @change="loadList" class="text-xs border rounded-lg px-2 py-1">
              <option value="">Tất cả nhân viên</option>
              <option v-for="e in employees" :key="e.name" :value="e.name">{{ e.employee_name }}</option>
            </select>
          </div>
          <div v-if="loading" class="flex items-center justify-center py-12"><LoadingIndicator /></div>
          <div v-else-if="!list.length" class="text-center text-gray-400 py-12 text-sm">
            <FeatherIcon name="trending-up" class="mx-auto mb-2 h-8 w-8 text-gray-300" />
            Chưa có đánh giá nào
          </div>
          <div v-else class="divide-y">
            <div v-for="a in list" :key="a.id" class="p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900 cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + a.employee)">{{ a.employee_name }}</span>
                  <span class="text-xs text-gray-400">· {{ a.period }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold" :class="scoreColor(a.score)">{{ a.score }}</span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full" :class="bandChip(a.band)">{{ a.band }}</span>
                </div>
              </div>
              <p v-if="a.remarks" class="text-sm text-gray-600 mt-1">{{ a.remarks }}</p>
              <div v-if="a.goals?.length" class="flex flex-wrap gap-1 mt-2">
                <span v-for="(g, gi) in a.goals" :key="gi" class="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600">🎯 {{ g }}</span>
              </div>
              <div class="text-xs text-gray-400 mt-1">{{ a.reviewer }} · {{ a.created }}</div>
            </div>
            <button @click="deleteAppraisal(a)" class="p-1 text-gray-300 hover:text-red-500 shrink-0" title="Xóa"><FeatherIcon name="trash-2" class="h-3.5 w-3.5" /></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Đánh giá mới -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showForm = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold mb-4">Đánh giá hiệu suất</h2>
        <div class="space-y-3">
          <div><label class="text-xs text-gray-500">Nhân viên <span class="text-red-400">*</span></label>
            <select v-model="form.employee" class="w-full border rounded-lg px-3 py-2 text-sm"><option value="">— Chọn —</option><option v-for="e in employees" :key="e.name" :value="e.name">{{ e.employee_name }}</option></select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-500">Kỳ đánh giá <span class="text-red-400">*</span></label><input v-model="form.period" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Q2/2026" /></div>
            <div><label class="text-xs text-gray-500">Điểm (0-100) <span class="text-red-400">*</span></label><input v-model.number="form.score" type="number" min="0" max="100" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="85" /></div>
          </div>
          <div v-if="form.score !== '' && form.score !== null" class="text-xs">Xếp loại: <span class="font-semibold" :class="scoreColor(form.score)">{{ bandOf(form.score) }}</span></div>
          <div><label class="text-xs text-gray-500">Mục tiêu (mỗi dòng 1 mục tiêu)</label><textarea v-model="form.goalsText" rows="3" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Tăng doanh số 20%&#10;Đào tạo nhân viên mới"></textarea></div>
          <div><label class="text-xs text-gray-500">Nhận xét</label><textarea v-model="form.remarks" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Nhận xét chung..."></textarea></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showForm = false">Hủy</Button>
          <Button @click="submit" :loading="saving">Lưu đánh giá</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const dash = ref({})
const list = ref([])
const employees = ref([])
const loading = ref(false)
const toast = ref('')
const filterEmployee = ref('')

const showForm = ref(false)
const saving = ref(false)
const showCycle = ref(false)
const cycleSaving = ref(false)
const cyForm = reactive({ period: '' })
const form = reactive({ employee: '', period: '', score: '', goalsText: '', remarks: '' })

const BANDS = [
  { key: 'Xuất sắc', color: 'bg-emerald-500' },
  { key: 'Tốt', color: 'bg-blue-500' },
  { key: 'Đạt', color: 'bg-amber-500' },
  { key: 'Cần cải thiện', color: 'bg-red-400' },
]
const bands = computed(() => BANDS.map(b => ({ ...b, count: dash.value.by_band?.[b.key] || 0 })))
const hasBands = computed(() => bands.value.some(b => b.count > 0))

function bandPct(count) {
  const max = Math.max(...bands.value.map(b => b.count), 1)
  return Math.max(4, Math.round(count / max * 100))
}

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }

function bandOf(s) {
  if (s >= 90) return 'Xuất sắc'; if (s >= 75) return 'Tốt'; if (s >= 60) return 'Đạt'; return 'Cần cải thiện'
}
function scoreColor(s) { if (s >= 90) return 'text-emerald-600'; if (s >= 75) return 'text-blue-600'; if (s >= 60) return 'text-amber-600'; return 'text-red-500' }
function bandChip(b) { return { 'Xuất sắc': 'bg-emerald-100 text-emerald-700', 'Tốt': 'bg-blue-100 text-blue-700', 'Đạt': 'bg-amber-100 text-amber-700', 'Cần cải thiện': 'bg-red-100 text-red-700' }[b] || 'bg-gray-100 text-gray-600' }

async function loadDash() {
  try { dash.value = await frappeRequest({ url: 'hr.api.get_performance_dashboard', method: 'GET', params: {} }) || {} } catch {}
}
async function loadList() {
  loading.value = true
  try { list.value = await frappeRequest({ url: 'hr.api.get_appraisals', method: 'GET', params: { employee: filterEmployee.value || undefined } }) || [] } catch {}
  loading.value = false
}

function openCycle() { showCycle.value = true }
async function doCycle() {
  cycleSaving.value = true
  try { const r = await frappeRequest({ url: 'hr.api.create_appraisal_cycle', method: 'POST', params: { period: cyForm.period } }); showCycle.value = false; showToast(`✅ Đã tạo ${r.created} đánh giá trống (${r.skipped} bỏ qua)`); await Promise.all([loadDash(), loadList()]) } catch (e) { showToast('❌ ' + (e.message || 'Lỗi'), 4000) }
  cycleSaving.value = false
}
function openForm() {
  Object.assign(form, { employee: '', period: '', score: '', goalsText: '', remarks: '' })
  showForm.value = true
}

async function deleteAppraisal(a) {
  if (!confirm('Xóa đánh giá ' + a.period + ' của ' + a.employee_name + '?')) return
  try { await frappeRequest({ url: 'hr.api.delete_appraisal', method: 'POST', params: { comment_name: a.id } }); showToast('✅ Đã xóa'); await Promise.all([loadDash(), loadList()]) } catch (e) { showToast('❌ ' + (e.message || 'Lỗi'), 4000) }
}

async function submit() {
  if (!form.employee || !form.period || form.score === '' || form.score === null) { showToast('❌ Điền nhân viên, kỳ và điểm'); return }
  saving.value = true
  try {
    const goals = form.goalsText.split('\n').map(g => g.trim()).filter(Boolean)
    await frappeRequest({ url: 'hr.api.create_appraisal', method: 'POST', params: {
      employee: form.employee, period: form.period, score: form.score,
      remarks: form.remarks, goals: JSON.stringify(goals),
    }})
    showForm.value = false
    showToast('✅ Đã lưu đánh giá')
    await Promise.all([loadDash(), loadList()])
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  saving.value = false
}

onMounted(async () => {
  await Promise.all([
    loadDash(),
    loadList(),
    frappeRequest({ url: 'hr.api.get_employees', method: 'GET', params: { page_length: 200 } }).then(d => employees.value = d || []).catch(() => {}),
  ])
})
</script>
