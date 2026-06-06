<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">Thâm niên</h1>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium bg-green-50 text-green-800 border border-green-200">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-4xl mx-auto space-y-4">
        <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <template v-else>
          <!-- Stats -->
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-2xl font-bold text-indigo-600">{{ data.total }}</div>
              <div class="text-xs text-gray-500 mt-0.5">Tổng nhân viên</div>
            </div>
            <div class="rounded-lg border bg-white p-4 shadow-sm text-center">
              <div class="text-2xl font-bold text-amber-600">{{ data.avg_years }}</div>
              <div class="text-xs text-gray-500 mt-0.5">Thâm niên TB (năm)</div>
            </div>
          </div>

          <!-- Phân nhóm + kỷ niệm -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="rounded-lg border bg-white shadow-sm p-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">📊 Phân nhóm thâm niên</h3>
              <div class="space-y-2">
                <div v-for="(count, band) in data.bands" :key="band" class="flex items-center gap-2 text-sm">
                  <span class="w-20 text-gray-600">{{ band }}</span>
                  <div class="flex-1 h-4 rounded-full bg-gray-100 overflow-hidden">
                    <div class="h-full rounded-full bg-amber-500 transition-all" :style="{ width: bandPct(count) + '%' }"></div>
                  </div>
                  <span class="w-6 text-right text-xs font-medium text-gray-700">{{ count }}</span>
                </div>
              </div>
            </div>

            <div class="rounded-lg border bg-white shadow-sm p-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">🎉 Kỷ niệm tháng này</h3>
              <div v-if="!data.anniversaries?.length" class="text-center text-gray-400 py-6 text-sm">Không có kỷ niệm tháng này</div>
              <div v-else class="space-y-2">
                <div v-for="x in data.anniversaries" :key="x.name" class="flex items-center justify-between text-sm">
                  <span class="font-medium text-gray-800 cursor-pointer hover:text-indigo-600" @click="$router.push('/employees/' + x.name)">{{ x.employee_name }}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{{ x.years }} năm · ngày {{ x.day }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Bảng xếp hạng -->
          <div class="rounded-lg border bg-white shadow-sm">
            <div class="px-4 py-3 border-b"><h2 class="text-sm font-semibold text-gray-700">🏅 Bảng xếp hạng thâm niên</h2></div>
            <div class="divide-y">
              <div v-for="(r, i) in data.ranking" :key="r.name" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50">
                <div class="w-7 text-center text-sm font-bold" :class="i < 3 ? 'text-amber-500' : 'text-gray-300'">{{ i + 1 }}</div>
                <div class="h-9 w-9 rounded-full flex items-center justify-center font-semibold text-white text-xs overflow-hidden" :class="avatarColor(r.employee_name)">
                  <img v-if="r.image" :src="r.image" class="h-full w-full object-cover" />
                  <span v-else>{{ initials(r.employee_name) }}</span>
                </div>
                <div class="flex-1 min-w-0 cursor-pointer" @click="$router.push('/employees/' + r.name)">
                  <div class="font-medium text-gray-900 truncate hover:text-indigo-600">{{ r.employee_name }}</div>
                  <div class="text-xs text-gray-400">{{ r.designation || '—' }} · vào {{ $fmtDate(r.date_of_joining) }}</div>
                </div>
                <span class="text-sm font-semibold text-amber-600 shrink-0">{{ r.years }} năm</span>
                <button @click="openAward(r)" class="p-1.5 rounded bg-amber-50 text-amber-600 hover:bg-amber-100 shrink-0" title="Khen thưởng"><FeatherIcon name="award" class="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Modal khen thưởng -->
    <div v-if="showAward" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="showAward = false">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-1">Khen thưởng</h2>
        <p class="text-xs text-gray-500 mb-4">{{ awardTarget?.employee_name }}</p>
        <div class="space-y-3">
          <div><label class="text-xs text-gray-500">Danh hiệu <span class="text-red-400">*</span></label><input v-model="awardForm.title" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="VD: Nhân viên xuất sắc Q2/2026" /></div>
          <div><label class="text-xs text-gray-500">Ghi chú</label><textarea v-model="awardForm.note" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Lý do khen thưởng..."></textarea></div>
        </div>
        <div class="flex justify-end gap-2 mt-5">
          <Button variant="subtle" @click="showAward = false">Hủy</Button>
          <Button @click="submitAward" :loading="saving">Ghi nhận</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const data = ref({ ranking: [], bands: {}, anniversaries: [] })
const loading = ref(true)
const toast = ref('')

const showAward = ref(false)
const saving = ref(false)
const awardTarget = ref(null)
const awardForm = reactive({ title: '', note: '' })

const maxBand = computed(() => Math.max(...Object.values(data.value.bands || { x: 1 }), 1))
function bandPct(c) { return Math.max(4, Math.round(c / maxBand.value * 100)) }

function showToast(msg) { toast.value = msg; setTimeout(() => toast.value = '', 3000) }
function initials(name) {
  if (!name) return '?'
  const clean = name.replace(/[^\p{L}\p{N}\s]/gu, '').replace(/\s+/g, ' ').trim()
  if (!clean) return '?'
  const p = clean.split(/\s+/)
  return ((p[0]?.[0] || '') + (p[p.length - 1]?.[0] || '')).toUpperCase()
}
const AVATAR_COLORS = ['bg-indigo-500', 'bg-emerald-500', 'bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-amber-500', 'bg-cyan-500', 'bg-rose-500']
function avatarColor(name) { let h = 0; for (const c of (name || '')) h = (h * 31 + c.charCodeAt(0)) >>> 0; return AVATAR_COLORS[h % AVATAR_COLORS.length] }

function openAward(r) { awardTarget.value = r; awardForm.title = ''; awardForm.note = ''; showAward.value = true }

async function submitAward() {
  if (!awardForm.title.trim()) { showToast('❌ Nhập danh hiệu'); return }
  saving.value = true
  try {
    await frappeRequest({ url: 'hr.api.add_award', method: 'POST', params: { employee: awardTarget.value.name, title: awardForm.title, note: awardForm.note } })
    showAward.value = false
    showToast('✅ Đã ghi nhận khen thưởng')
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi')) }
  saving.value = false
}

async function load() {
  try { data.value = await frappeRequest({ url: 'hr.api.get_seniority', method: 'GET', params: {} }) || data.value } catch {}
  loading.value = false
}
onMounted(load)
</script>
