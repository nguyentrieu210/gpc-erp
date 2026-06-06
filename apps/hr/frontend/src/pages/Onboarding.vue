<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-violet-50 flex flex-col">

    <!-- Header Banner -->
    <div class="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 text-white py-6 px-4 shadow-lg">
      <div class="max-w-2xl mx-auto flex items-center gap-4">
        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center shadow-inner">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-extrabold tracking-tight">Điền thông tin hồ sơ nhân viên</h1>
          <p class="text-sm text-indigo-100 mt-0.5">Hoàn tất trước ngày nhận việc để bộ phận HR chuẩn bị đầy đủ</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center space-y-3">
        <div class="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="text-gray-500 text-sm font-medium">Đang tải thông tin...</p>
      </div>
    </div>

    <!-- Error: Invalid token -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center px-4">
      <div class="max-w-sm text-center space-y-4">
        <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 class="text-lg font-bold text-gray-800">Link không hợp lệ</h2>
        <p class="text-sm text-gray-500">{{ error }}</p>
        <p class="text-xs text-gray-400">Vui lòng liên hệ bộ phận nhân sự để được hỗ trợ.</p>
      </div>
    </div>

    <!-- Already Done -->
    <div v-else-if="alreadyDone" class="flex-1 flex items-center justify-center px-4">
      <div class="max-w-sm text-center space-y-4">
        <div class="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto animate-bounce-once">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-lg font-bold text-gray-800">Đã hoàn thành!</h2>
        <p class="text-sm text-gray-500">Bạn đã điền thông tin hồ sơ thành công. Bộ phận HR sẽ liên hệ bạn sớm.</p>
        <p class="text-xs text-gray-400">Nếu cần cập nhật thông tin, vui lòng liên hệ trực tiếp HR.</p>
      </div>
    </div>

    <!-- Success Submitted -->
    <div v-else-if="submitted" class="flex-1 flex items-center justify-center px-4">
      <div class="max-w-sm text-center space-y-4">
        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center mx-auto shadow-lg shadow-emerald-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-xl font-extrabold text-gray-800">Gửi thành công!</h2>
        <p class="text-sm text-gray-600">Cảm ơn <strong>{{ applicantName }}</strong> đã hoàn thành điền thông tin hồ sơ.</p>
        <p class="text-sm text-gray-500">Bộ phận HR sẽ xem xét và liên hệ bạn để xác nhận thông tin trước ngày nhận việc.</p>
        <div class="mt-4 p-3 bg-indigo-50 rounded-xl border border-indigo-100 text-left">
          <p class="text-xs text-indigo-700 font-semibold">Vị trí: {{ applicantDesignation }}</p>
          <p class="text-xs text-indigo-600 mt-1">Phòng ban: {{ applicantDepartment }}</p>
        </div>
      </div>
    </div>

    <!-- The Form -->
    <div v-else class="flex-1 py-8 px-4">
      <div class="max-w-2xl mx-auto space-y-6">

        <!-- Welcome Card -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-extrabold text-xl shadow-md shadow-indigo-200 shrink-0">
            {{ initials(applicantName) }}
          </div>
          <div>
            <p class="text-xs text-gray-500 font-medium">Chào mừng</p>
            <h2 class="text-base font-extrabold text-gray-900">{{ applicantName }}</h2>
            <p class="text-xs text-indigo-600 font-semibold mt-0.5">{{ applicantDesignation }} · {{ applicantDepartment }}</p>
          </div>
        </div>

        <!-- Progress indicator -->
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-500"
              :style="{ width: progressPct + '%' }"></div>
          </div>
          <span class="shrink-0 font-semibold text-indigo-600">{{ filledFields }} / {{ totalFields }} mục</span>
        </div>

        <!-- SECTION 1: Thông tin cá nhân -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-indigo-50 to-violet-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold">1</div>
            <h3 class="text-sm font-bold text-gray-800">Thông tin cá nhân</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Họ và tên đầy đủ <span class="text-red-400">*</span></label>
              <input v-model="form.full_name" type="text" class="field-input" placeholder="VD: Nguyễn Văn An" readonly />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Ngày sinh <span class="text-red-400">*</span></label>
              <input v-model="form.date_of_birth" type="date" class="field-input" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Giới tính <span class="text-red-400">*</span></label>
              <select v-model="form.gender" class="field-input">
                <option value="">-- Chọn --</option>
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
                <option value="Khác">Khác</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Dân tộc</label>
              <input v-model="form.ethnicity" type="text" class="field-input" placeholder="VD: Kinh" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Tôn giáo</label>
              <input v-model="form.religion" type="text" class="field-input" placeholder="VD: Không" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Quốc tịch</label>
              <input v-model="form.nationality" type="text" class="field-input" placeholder="VD: Việt Nam" />
            </div>
          </div>
        </div>

        <!-- SECTION 2: CCCD / Giấy tờ tùy thân -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center text-xs font-bold">2</div>
            <h3 class="text-sm font-bold text-gray-800">CCCD / Giấy tờ tùy thân</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Số CCCD / CMND <span class="text-red-400">*</span></label>
              <input v-model="form.id_number" type="text" class="field-input" placeholder="VD: 0123456789XX" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Ngày cấp <span class="text-red-400">*</span></label>
              <input v-model="form.id_issue_date" type="date" class="field-input" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Nơi cấp</label>
              <input v-model="form.id_issue_place" type="text" class="field-input" placeholder="VD: Cục Cảnh sát QLHC về TTXH - Bộ Công an" />
            </div>
          </div>
        </div>

        <!-- SECTION 3: Liên hệ & Địa chỉ -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold">3</div>
            <h3 class="text-sm font-bold text-gray-800">Thông tin liên hệ & Địa chỉ</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Email cá nhân</label>
              <input v-model="form.email" type="email" class="field-input" readonly />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Số điện thoại <span class="text-red-400">*</span></label>
              <input v-model="form.phone" type="tel" class="field-input" placeholder="VD: 0901234567" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Địa chỉ thường trú</label>
              <input v-model="form.permanent_address" type="text" class="field-input" placeholder="VD: 123 Đường ABC, Phường XYZ, TP.HCM" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Địa chỉ tạm trú (nếu khác)</label>
              <input v-model="form.current_address" type="text" class="field-input" placeholder="Bỏ trống nếu giống thường trú" />
            </div>
          </div>
        </div>

        <!-- SECTION 4: Tài khoản ngân hàng -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">4</div>
            <h3 class="text-sm font-bold text-gray-800">Tài khoản ngân hàng (nhận lương)</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Tên ngân hàng</label>
              <input v-model="form.bank_name" type="text" class="field-input" placeholder="VD: Vietcombank, BIDV, MB..." />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Số tài khoản</label>
              <input v-model="form.bank_account" type="text" class="field-input" placeholder="VD: 1234567890" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Chi nhánh</label>
              <input v-model="form.bank_branch" type="text" class="field-input" placeholder="VD: Chi nhánh Hồ Chí Minh" />
            </div>
          </div>
        </div>

        <!-- SECTION 5: Bảo hiểm xã hội -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-purple-50 to-violet-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center text-xs font-bold">5</div>
            <h3 class="text-sm font-bold text-gray-800">Bảo hiểm xã hội</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Số sổ BHXH (nếu có)</label>
              <input v-model="form.social_insurance_number" type="text" class="field-input" placeholder="VD: 0112345678" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Nơi đăng ký KCB ban đầu</label>
              <input v-model="form.health_insurance_place" type="text" class="field-input" placeholder="VD: BV Quận 1 TP.HCM" />
            </div>
          </div>
        </div>

        <!-- SECTION 6: Người thân liên hệ khẩn cấp -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 bg-gradient-to-r from-rose-50 to-pink-50 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-rose-100 text-rose-600 flex items-center justify-center text-xs font-bold">6</div>
            <h3 class="text-sm font-bold text-gray-800">Người liên hệ khẩn cấp</h3>
          </div>
          <div class="p-5 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Họ tên</label>
              <input v-model="form.emergency_name" type="text" class="field-input" placeholder="VD: Nguyễn Văn B" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Quan hệ</label>
              <input v-model="form.emergency_relation" type="text" class="field-input" placeholder="VD: Vợ/Chồng/Cha/Mẹ" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 mb-1.5">Số điện thoại</label>
              <input v-model="form.emergency_phone" type="tel" class="field-input" placeholder="VD: 0901234567" />
            </div>
          </div>
        </div>

        <!-- SECTION 7: Ghi chú bổ sung -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-3.5 border-b border-gray-200 flex items-center gap-2">
            <div class="w-6 h-6 rounded-lg bg-gray-100 text-gray-600 flex items-center justify-center text-xs font-bold">7</div>
            <h3 class="text-sm font-bold text-gray-800">Ghi chú khác</h3>
          </div>
          <div class="p-5">
            <textarea v-model="form.notes" rows="3" class="field-input resize-none" placeholder="Ghi chú thêm nếu có (dị ứng thuốc, yêu cầu đặc biệt...)"></textarea>
          </div>
        </div>

        <!-- Error message -->
        <div v-if="submitError" class="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ submitError }}
        </div>

        <!-- Submit Button -->
        <button @click="submitForm" :disabled="submitting || !canSubmit"
          class="w-full py-3.5 rounded-2xl font-bold text-sm tracking-wide transition-all duration-200 shadow-lg flex items-center justify-center gap-2"
          :class="canSubmit ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:from-indigo-700 hover:to-violet-700 hover:shadow-indigo-200 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0' : 'bg-gray-200 text-gray-400 cursor-not-allowed'">
          <span v-if="submitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ submitting ? 'Đang gửi...' : 'Gửi thông tin hồ sơ' }}
        </button>

        <p class="text-center text-xs text-gray-400 pb-6">
          Thông tin của bạn được bảo mật và chỉ dùng để chuẩn bị hồ sơ nhân viên.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const token = ref('')
const loading = ref(true)
const error = ref('')
const alreadyDone = ref(false)
const submitted = ref(false)
const submitting = ref(false)
const submitError = ref('')

const applicantName = ref('')
const applicantDesignation = ref('')
const applicantDepartment = ref('')

const form = ref({
  full_name: '',
  date_of_birth: '',
  gender: '',
  ethnicity: 'Kinh',
  religion: 'Không',
  nationality: 'Việt Nam',
  id_number: '',
  id_issue_date: '',
  id_issue_place: '',
  email: '',
  phone: '',
  permanent_address: '',
  current_address: '',
  bank_name: '',
  bank_account: '',
  bank_branch: '',
  social_insurance_number: '',
  health_insurance_place: '',
  emergency_name: '',
  emergency_relation: '',
  emergency_phone: '',
  notes: '',
})

const requiredFields = ['date_of_birth', 'gender', 'id_number', 'id_issue_date', 'phone']

const canSubmit = computed(() => {
  return requiredFields.every(f => form.value[f] && String(form.value[f]).trim())
})

const filledFields = computed(() => {
  return Object.values(form.value).filter(v => v && String(v).trim()).length
})

const totalFields = computed(() => Object.keys(form.value).length)

const progressPct = computed(() => Math.round((filledFields.value / totalFields.value) * 100))

function initials(name) {
  if (!name) return '?'
  const clean = name.replace(/[^\p{L}\p{N}\s]/gu, '').trim()
  const parts = clean.split(/\s+/)
  if (parts.length >= 2) return (parts[parts.length - 2][0] + parts[parts.length - 1][0]).toUpperCase()
  return parts[0].slice(0, 2).toUpperCase()
}

async function callApi(url, params = {}) {
  const query = new URLSearchParams({ ...params, cmd: url }).toString()
  const res = await fetch(`/api/method/${url}?${query}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const json = await res.json()
  return json.message ?? json
}

onMounted(async () => {
  const urlParams = new URLSearchParams(window.location.search)
  token.value = urlParams.get('token') || ''
  if (!token.value) {
    error.value = 'Không tìm thấy token trong URL.'
    loading.value = false
    return
  }
  try {
    const data = await callApi('hr.api.get_onboarding_form', { token: token.value })
    if (data?.error) {
      error.value = data.error
    } else if (data?.already_done) {
      alreadyDone.value = true
      applicantName.value = data.applicant_name
      applicantDesignation.value = data.designation
      applicantDepartment.value = data.department
    } else {
      applicantName.value = data.applicant_name || ''
      applicantDesignation.value = data.designation || ''
      applicantDepartment.value = data.department || ''
      form.value.full_name = data.applicant_name || ''
      form.value.email = data.email_id || ''
      form.value.phone = data.phone_number || ''
      // Pre-fill from existing data if any
      if (data.existing_data) {
        Object.assign(form.value, data.existing_data)
      }
    }
  } catch (e) {
    error.value = 'Không thể kết nối máy chủ. Vui lòng thử lại sau.'
  }
  loading.value = false
})

async function submitForm() {
  if (!canSubmit.value || submitting.value) return
  submitError.value = ''
  submitting.value = true
  try {
    const res = await fetch('/api/method/hr.api.submit_onboarding_form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': 'fetch' },
      body: JSON.stringify({ token: token.value, data: JSON.stringify(form.value) })
    })
    const json = await res.json()
    const msg = json.message ?? json
    if (msg?.error) {
      submitError.value = msg.error
    } else if (msg?.ok) {
      submitted.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      submitError.value = 'Đã có lỗi xảy ra, vui lòng thử lại.'
    }
  } catch (e) {
    submitError.value = 'Lỗi kết nối. Vui lòng kiểm tra internet và thử lại.'
  }
  submitting.value = false
}
</script>

<style scoped>
.field-input {
  @apply w-full border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white transition placeholder-gray-300;
  outline: none;
}
.field-input:focus {
  border-color: #a5b4fc;
  box-shadow: 0 0 0 2px #e0e7ff;
}
.field-input[readonly] {
  @apply bg-gray-50 text-gray-500;
}
</style>
