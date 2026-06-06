<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Ngân sách (Dự toán)" icon="target" icon-class="text-orange-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo ngân sách</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-3">
      <div class="app-card p-4">
        <div class="text-sm font-semibold mb-2">Chênh lệch ngân sách vs thực tế <span class="text-xs text-gray-400">({{ variance.fiscal_year || '' }})</span></div>
        <table class="w-full text-sm">
          <thead><tr><th class="px-2 py-1 text-left">TK</th><th class="px-2 py-1 text-left">Bộ phận</th><th class="px-2 py-1 text-right">Dự toán</th><th class="px-2 py-1 text-right">Thực tế</th><th class="px-2 py-1 text-right">Chênh lệch</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in variance.rows || []" :key="i">
              <td class="px-2 py-1.5">{{ r.account_name }}</td><td class="px-2 py-1.5 text-gray-500">{{ r.cost_center }}</td>
              <td class="px-2 py-1.5 text-right">{{ money(r.budget_amount) }}</td><td class="px-2 py-1.5 text-right">{{ money(r.actual) }}</td>
              <td class="px-2 py-1.5 text-right font-medium" :class="r.variance >= 0 ? 'text-emerald-600' : 'text-rose-600'">{{ money(r.variance) }}</td>
            </tr>
            <tr v-if="!(variance.rows || []).length"><td colspan="5" class="py-4 text-center text-gray-400">Chưa có ngân sách đã duyệt</td></tr>
          </tbody>
        </table>
      </div>
      <div class="app-card p-4">
        <div class="text-sm font-semibold mb-2">Danh sách ngân sách</div>
        <div v-for="b in budgets" :key="b.name" class="flex items-center px-2 py-2 text-sm border-b last:border-0">
          <span class="flex-1">{{ b.name }} · {{ b.cost_center }}</span><span class="text-gray-500">{{ b.fiscal_year }}</span>
          <StatusBadge class="ml-2" :status="b.docstatus === 1 ? 'Đã duyệt' : 'Nháp'" />
        </div>
        <div v-if="!budgets.length" class="text-sm text-gray-400 py-2">Chưa có ngân sách</div>
      </div>
    </main>

    <FormModal :show="show" title="Tạo ngân sách" icon="target" width="max-w-2xl" hide-footer @close="show = false">
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">Bộ phận (Cost Center) *</label><EntityPicker v-model="form.cost_center" api="tckt.api.get_cost_centers" result-key="entries" value-key="name" label-key="cost_center_name" /></div>
          <div><label class="text-xs text-gray-500">Năm tài chính</label><select v-model="form.fiscal_year" class="inp"><option v-for="fy in fiscalYears" :key="fy" :value="fy">{{ fy }}</option></select></div>
        </div>
        <div>
          <label class="text-xs text-gray-500">Dự toán theo tài khoản</label>
          <div class="rounded-lg border bg-white overflow-hidden">
            <table class="w-full text-sm"><thead><tr><th class="px-2 py-2 text-left">Tài khoản</th><th class="px-2 py-2 text-right w-40">Số tiền dự toán</th><th class="w-8"></th></tr></thead>
              <tbody><tr v-for="(ln, i) in form.lines" :key="i">
                <td class="px-2 py-1.5"><EntityPicker v-model="ln.account" api="tckt.api.get_accounts" result-key="entries" value-key="name" label-key="label" :params="{ root_type: 'Expense' }" :display-text="ln.label" /></td>
                <td class="px-2 py-1.5"><input v-model.number="ln.budget_amount" type="number" min="0" class="inp text-right" /></td>
                <td class="px-2 py-1.5 text-center"><button class="text-gray-400 hover:text-rose-500" @click="form.lines.splice(i, 1)"><FeatherIcon name="trash-2" class="h-4 w-4" /></button></td>
              </tr></tbody>
            </table>
          </div>
          <button class="btn-secondary px-3 py-1.5 rounded-lg text-sm mt-2 inline-flex items-center gap-1" @click="form.lines.push({ account: '', label: '', budget_amount: 0 })"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm dòng</button>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
        <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving" @click="save">{{ saving ? 'Đang lưu…' : 'Lưu & duyệt' }}</button>
      </template>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, FormModal, EntityPicker, StatusBadge, useToast, callApi, money } from '@shared'
const { toast, ok, err } = useToast()
const budgets = ref([]); const fiscalYears = ref([]); const variance = ref({ rows: [] })
async function reload() {
  const b = await callApi('tckt.api.get_budgets', {}, 'GET'); budgets.value = b?.entries || []; fiscalYears.value = b?.fiscal_years || []
  variance.value = await callApi('tckt.api.get_budget_variance', {}, 'GET') || { rows: [] }
}
reload()
const show = ref(false); const saving = ref(false)
const form = reactive({ cost_center: '', fiscal_year: '', lines: [] })
function openCreate() { form.cost_center = ''; form.fiscal_year = fiscalYears.value[0] || ''; form.lines = [{ account: '', label: '', budget_amount: 0 }]; show.value = true }
async function save() {
  const lines = form.lines.filter((l) => l.account && l.budget_amount)
  if (!form.cost_center) return err('Chọn bộ phận')
  if (!lines.length) return err('Thêm ít nhất 1 dòng dự toán')
  saving.value = true
  try {
    for (const l of lines) {
      await callApi('tckt.api.create_budget', { cost_center: form.cost_center, account: l.account, budget_amount: l.budget_amount, fiscal_year: form.fiscal_year || undefined, submit: 1 })
    }
    ok('Đã tạo ngân sách'); show.value = false; reload()
  } catch (e) { err(e?.message || 'Lỗi') } finally { saving.value = false }
}
</script>
