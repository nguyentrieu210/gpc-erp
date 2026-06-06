<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Phiếu kế toán (Nhật ký)" icon="edit-3" icon-class="text-green-600">
      <button class="btn-primary px-3 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-1" @click="openCreate"><FeatherIcon name="plus" class="h-4 w-4" /> Tạo phiếu</button>
    </PageHeader>
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full">
      <DataTable :rows="rows" :columns="columns" :loading="loading" search-placeholder="Tìm số phiếu / diễn giải…" :search-keys="['name', 'user_remark']" :filters="filterDefs" @row-click="goDetail">
        <template #col-total_debit="{ value }"><span class="font-semibold">{{ fmtVnd(value) }}</span></template>
        <template #col-docstatus="{ row }"><StatusBadge :status="row.docstatus === 1 ? 'Đã ghi sổ' : (row.docstatus === 2 ? 'Đã hủy' : 'Nháp')" /></template>
        <template #col-posting_date="{ value }">{{ $fmtDate(value) }}</template>
      </DataTable>
    </main>

    <FormModal :show="show" title="Tạo phiếu kế toán" icon="edit-3" width="max-w-3xl" hide-footer @close="show = false">
      <div class="space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">Ngày hạch toán</label><input v-model="form.posting_date" type="date" class="inp" /></div>
          <div><label class="text-xs text-gray-500">Diễn giải</label><input v-model="form.remark" class="inp" placeholder="Nội dung bút toán…" /></div>
        </div>
        <div>
          <label class="text-xs text-gray-500">Định khoản</label>
          <div class="rounded-lg border bg-white overflow-hidden">
            <table class="w-full text-sm">
              <thead><tr><th class="px-2 py-2 text-left">Tài khoản</th><th class="px-2 py-2 text-right w-32">Nợ</th><th class="px-2 py-2 text-right w-32">Có</th><th class="w-8"></th></tr></thead>
              <tbody>
                <tr v-for="(ln, i) in form.lines" :key="i">
                  <td class="px-2 py-1.5 min-w-[220px]"><EntityPicker v-model="ln.account" api="tckt.api.get_accounts" result-key="entries" value-key="name" label-key="label" sub-key="account_type" :display-text="ln.label" placeholder="Chọn TK…" /></td>
                  <td class="px-2 py-1.5"><input v-model.number="ln.debit" type="number" min="0" step="any" class="inp text-right" @input="ln.credit = ln.debit ? 0 : ln.credit" /></td>
                  <td class="px-2 py-1.5"><input v-model.number="ln.credit" type="number" min="0" step="any" class="inp text-right" @input="ln.debit = ln.credit ? 0 : ln.debit" /></td>
                  <td class="px-2 py-1.5 text-center"><button class="text-gray-400 hover:text-rose-500" @click="form.lines.splice(i, 1)"><FeatherIcon name="trash-2" class="h-4 w-4" /></button></td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="bg-gray-50 font-semibold">
                  <td class="px-2 py-2 text-right">Tổng</td>
                  <td class="px-2 py-2 text-right">{{ money(totalDr) }}</td>
                  <td class="px-2 py-2 text-right">{{ money(totalCr) }}</td><td></td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="flex items-center justify-between mt-2">
            <button class="btn-secondary px-3 py-1.5 rounded-lg text-sm inline-flex items-center gap-1" @click="addLine"><FeatherIcon name="plus" class="h-4 w-4" /> Thêm dòng</button>
            <span class="text-sm" :class="balanced ? 'text-emerald-600' : 'text-rose-600'">{{ balanced ? '✓ Cân đối' : 'Lệch ' + money(Math.abs(totalDr - totalCr)) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="show = false">Hủy</button>
        <button class="btn-secondary px-4 py-2 rounded-lg text-sm" :disabled="saving" @click="save(0)">Lưu nháp</button>
        <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium" :disabled="saving || !balanced || totalDr === 0" @click="save(1)">{{ saving ? 'Đang lưu…' : 'Lưu & ghi sổ' }}</button>
      </template>
    </FormModal>
    <div v-if="toast" class="fixed top-16 right-4 z-[60] px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'">{{ toast }}</div>
  </div>
</template>
<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import { PageHeader, DataTable, FormModal, EntityPicker, StatusBadge, useToast, callApi, fmtVnd, money, today } from '@shared'
const router = useRouter(); const { toast, ok, err } = useToast()
const rows = ref([]); const loading = ref(false)
const columns = [
  { key: 'name', label: 'Số phiếu' }, { key: 'posting_date', label: 'Ngày' },
  { key: 'user_remark', label: 'Diễn giải' }, { key: 'total_debit', label: 'Số tiền', align: 'right' },
  { key: 'docstatus', label: 'Trạng thái' },
]
const filterDefs = [{ key: 'docstatus', label: 'Trạng thái', options: [{ value: '0', label: 'Nháp' }, { value: '1', label: 'Đã ghi sổ' }, { value: '2', label: 'Đã hủy' }] }]
async function reload() { loading.value = true; try { rows.value = (await callApi('tckt.api.get_journal_entries', { page_length: 200 }, 'GET'))?.entries || [] } finally { loading.value = false } }
reload()
const show = ref(false); const saving = ref(false)
const form = reactive({ posting_date: today(), remark: '', lines: [] })
const totalDr = computed(() => form.lines.reduce((s, l) => s + Number(l.debit || 0), 0))
const totalCr = computed(() => form.lines.reduce((s, l) => s + Number(l.credit || 0), 0))
const balanced = computed(() => totalDr.value > 0 && Math.abs(totalDr.value - totalCr.value) < 0.5)
function addLine() { form.lines.push({ account: '', label: '', debit: 0, credit: 0 }) }
function openCreate() { form.posting_date = today(); form.remark = ''; form.lines = [{ account: '', label: '', debit: 0, credit: 0 }, { account: '', label: '', debit: 0, credit: 0 }]; show.value = true }
async function save(submit) {
  const lines = form.lines.filter((l) => l.account && (l.debit || l.credit))
  if (lines.length < 2) return err('Cần ít nhất 2 dòng định khoản')
  if (submit && !balanced.value) return err('Bút toán chưa cân đối')
  saving.value = true
  try {
    const je = await callApi('tckt.api.create_journal_entry', { accounts: JSON.stringify(lines.map((l) => ({ account: l.account, debit: l.debit || 0, credit: l.credit || 0 }))), posting_date: form.posting_date, remark: form.remark, submit })
    ok(submit ? 'Đã ghi sổ ' + je.name : 'Đã lưu nháp'); show.value = false; reload()
  } catch (e) { err(e?.message || 'Lỗi') } finally { saving.value = false }
}
function goDetail(row) { router.push('/journal-entries/' + row.name) }
</script>
