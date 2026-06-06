<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Cấu hình lương VN</h1>
      <Button size="sm" @click="save" :loading="saving"><FeatherIcon name="save" class="h-4 w-4" /> Lưu</Button>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium"
      :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else class="max-w-3xl mx-auto space-y-4">
        <p class="text-xs text-gray-500">Các mức theo quy định Nhà nước — chỉnh khi Nghị định/Luật thay đổi. Tỷ lệ nhập theo %.</p>

        <!-- Mức cơ sở -->
        <section class="rounded-xl border bg-white p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-700 mb-3">Mức cơ sở & giảm trừ</h2>
          <div class="grid sm:grid-cols-2 gap-3 text-sm">
            <label class="block"><span class="text-xs text-gray-500">Lương cơ sở (trần BHXH/BHYT = 20×)</span><input v-model.number="f.luong_co_so" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
            <label class="block"><span class="text-xs text-gray-500">Hệ số trần đóng BH</span><input v-model.number="f.he_so_tran" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
            <label class="block"><span class="text-xs text-gray-500">Giảm trừ bản thân/tháng</span><input v-model.number="f.gt_ban_than" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
            <label class="block"><span class="text-xs text-gray-500">Giảm trừ người phụ thuộc/người</span><input v-model.number="f.gt_npt" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
            <label class="block"><span class="text-xs text-gray-500">Miễn thuế ăn ca/tháng</span><input v-model.number="f.mien_an_ca" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
          </div>
        </section>

        <!-- Lương tối thiểu vùng -->
        <section class="rounded-xl border bg-white p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-700 mb-3">Lương tối thiểu vùng (trần BHTN = 20×)</h2>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <label v-for="v in ['I','II','III','IV']" :key="v" class="block"><span class="text-xs text-gray-500">Vùng {{ v }}</span><input v-model.number="f.vung[v]" type="number" class="w-full border rounded-lg px-3 py-2" /></label>
          </div>
        </section>

        <!-- Tỷ lệ BH -->
        <section class="rounded-xl border bg-white p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-700 mb-3">Tỷ lệ bảo hiểm (%)</h2>
          <div class="grid grid-cols-3 gap-3 text-sm">
            <div></div><div class="text-xs font-medium text-gray-500 text-center">NLĐ đóng</div><div class="text-xs font-medium text-gray-500 text-center">DN đóng</div>
            <template v-for="k in ['bhxh','bhyt','bhtn']" :key="k">
              <div class="text-xs text-gray-600 self-center uppercase">{{ k }}</div>
              <input v-model.number="f.nld[k]" type="number" step="0.1" class="border rounded-lg px-3 py-2" />
              <input v-model.number="f.dn[k]" type="number" step="0.1" class="border rounded-lg px-3 py-2" />
            </template>
          </div>
        </section>

        <!-- Biểu thuế TNCN -->
        <section class="rounded-xl border bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-700">Biểu thuế TNCN lũy tiến</h2>
            <button @click="f.brackets.push({ den: null, suat: 0 })" class="text-xs text-indigo-600">+ Thêm bậc</button>
          </div>
          <div class="space-y-1.5">
            <div class="grid grid-cols-[1fr_1fr_auto] gap-2 text-xs text-gray-400 px-1"><span>Đến mức TNTT/tháng (trống = trở lên)</span><span>Thuế suất (%)</span><span></span></div>
            <div v-for="(b, i) in f.brackets" :key="i" class="grid grid-cols-[1fr_1fr_auto] gap-2 items-center">
              <input v-model.number="b.den" type="number" class="border rounded-lg px-3 py-1.5 text-sm" placeholder="(trở lên)" />
              <input v-model.number="b.suat" type="number" step="0.1" class="border rounded-lg px-3 py-1.5 text-sm" />
              <button @click="f.brackets.splice(i,1)" class="text-gray-400 hover:text-red-500"><FeatherIcon name="x" class="h-4 w-4" /></button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const loading = ref(true)
const saving = ref(false)
const toast = ref('')
const raw = ref({})
const f = reactive({ luong_co_so: 0, he_so_tran: 20, gt_ban_than: 0, gt_npt: 0, mien_an_ca: 0,
  vung: { I: 0, II: 0, III: 0, IV: 0 }, nld: { bhxh: 0, bhyt: 0, bhtn: 0 }, dn: { bhxh: 0, bhyt: 0, bhtn: 0 }, brackets: [] })

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }

async function loadCfg() {
  try {
    const c = await frappeRequest({ url: 'hr.api.get_vn_payroll_config', method: 'GET', params: {} })
    raw.value = c
    f.luong_co_so = c.luong_co_so; f.he_so_tran = c.he_so_tran
    f.gt_ban_than = c.giam_tru_ban_than; f.gt_npt = c.giam_tru_nguoi_phu_thuoc; f.mien_an_ca = c.mien_thue_an_ca
    f.vung = { ...c.luong_toi_thieu_vung }
    f.nld = { bhxh: c.ty_le_bh_nld.bhxh * 100, bhyt: c.ty_le_bh_nld.bhyt * 100, bhtn: c.ty_le_bh_nld.bhtn * 100 }
    f.dn = { bhxh: c.ty_le_bh_dn.bhxh * 100, bhyt: c.ty_le_bh_dn.bhyt * 100, bhtn: c.ty_le_bh_dn.bhtn * 100 }
    f.brackets = (c.pit_brackets || []).map(([den, suat]) => ({ den, suat: suat * 100 }))
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi tải cấu hình'), 4000) }
  loading.value = false
}

async function save() {
  saving.value = true
  try {
    const cfg = {
      ...raw.value,
      luong_co_so: f.luong_co_so, he_so_tran: f.he_so_tran,
      giam_tru_ban_than: f.gt_ban_than, giam_tru_nguoi_phu_thuoc: f.gt_npt, mien_thue_an_ca: f.mien_an_ca,
      luong_toi_thieu_vung: { ...f.vung },
      ty_le_bh_nld: { bhxh: f.nld.bhxh / 100, bhyt: f.nld.bhyt / 100, bhtn: f.nld.bhtn / 100 },
      ty_le_bh_dn: { bhxh: f.dn.bhxh / 100, bhyt: f.dn.bhyt / 100, bhtn: f.dn.bhtn / 100 },
      pit_brackets: f.brackets.map(b => [b.den === '' || b.den === null ? null : Number(b.den), Number(b.suat) / 100]),
    }
    await frappeRequest({ url: 'hr.api.save_vn_payroll_config', method: 'POST', params: { config: JSON.stringify(cfg) } })
    showToast('✅ Đã lưu cấu hình lương')
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi lưu'), 4000) }
  saving.value = false
}

loadCfg()
</script>
