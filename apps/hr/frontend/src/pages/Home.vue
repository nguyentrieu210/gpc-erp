<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <FeatherIcon name="users" class="h-5 w-5 text-indigo-600" />
        <h1 class="text-lg font-semibold text-gray-900">Nhân sự</h1>
      </div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          <span>Cổng</span>
        </Button>
        <div class="h-4 w-[1px] bg-gray-200"></div>
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600 hover:text-red-700">
          Đăng xuất
        </Button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-4">
      <!-- Quick stats -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div class="rounded-lg border bg-white p-3 text-center shadow-sm" @click="$router.push('/employees')">
          <div class="text-xl font-bold text-indigo-600">{{ stats.employees }}</div>
          <div class="text-xs text-gray-500">Nhân viên</div>
        </div>
        <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
          <div class="text-xl font-bold text-green-600">{{ stats.present }}</div>
          <div class="text-xs text-gray-500">Đi làm hôm nay</div>
        </div>
        <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
          <div class="text-xl font-bold text-amber-600">{{ stats.on_leave }}</div>
          <div class="text-xs text-gray-500">Đang nghỉ phép</div>
        </div>
        <div class="rounded-lg border bg-white p-3 text-center shadow-sm" @click="$router.push('/recruitment')">
          <div class="text-xl font-bold text-blue-600">{{ stats.openings }}</div>
          <div class="text-xs text-gray-500">Vị trí tuyển dụng</div>
        </div>
      </div>

      <!-- Module launcher -->
      <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">Phân hệ</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="m in modules" :key="m.key"
          class="group rounded-xl border bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md cursor-pointer relative overflow-hidden"
          :class="m.route ? '' : 'opacity-50'"
          @click="m.route ? $router.push(m.route) : null">
          <span v-if="!m.route" class="absolute top-3 right-3 text-[10px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 font-medium">Sắp ra mắt</span>
          <span v-else-if="m.new" class="absolute top-3 right-3 text-[10px] px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">Mới</span>

          <div class="flex items-start gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg">
              <FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 group-hover:text-indigo-600 transition">{{ m.name }}</h3>
              <p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p>
              <div v-if="m.count !== undefined" class="mt-2 text-xs font-medium" :class="m.color">{{ m.count }} bản ghi</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, FeatherIcon, frappeRequest, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)

function goPortal() {
  window.location.href = '/portal_app'
}

async function logout() {
  loggingOut.value = true
  try {
    await fetch('/api/method/portal.api.portal_logout', { method: 'GET', credentials: 'include' })
  } catch (e) {
    // ignore
  }
  // Clear cookies manually in JS
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i];
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=" + window.location.hostname;
    const parts = window.location.hostname.split('.');
    if (parts.length >= 2) {
      const domain = '.' + parts.slice(-2).join('.');
      document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=" + domain;
    }
  }
  window.location.href = '/portal_app/login'
}

const { data: homeStats } = useFrappeApi('hr.api.get_hr_home_stats', { initialData: { employees: 0, present: 0, on_leave: 0, openings: 0 } })

const stats = computed(() => ({
  employees: homeStats.value?.employees ?? 0,
  present: homeStats.value?.present ?? 0,
  on_leave: homeStats.value?.on_leave ?? 0,
  openings: homeStats.value?.openings ?? 0,
}))

const modules = [
  { key: 'employees',   name: 'Quản lý nhân sự',   desc: 'Hồ sơ, hợp đồng, thông tin nhân viên',         icon: 'users',          color: 'text-indigo-600',   bg: 'bg-indigo-100',   route: '/employees' },
  { key: 'leaves',      name: 'Nghỉ phép',          desc: 'Đơn nghỉ phép, phê duyệt, số dư phép',         icon: 'calendar',       color: 'text-green-600',    bg: 'bg-green-100',    route: '/leaves' },
  { key: 'recruitment', name: 'Tuyển dụng',          desc: 'Vị trí tuyển dụng, ứng viên, phỏng vấn',        icon: 'user-plus',      color: 'text-blue-600',     bg: 'bg-blue-100',     route: '/recruitment', new: true },
  { key: 'attendance',  name: 'Ca làm & Chấm công',  desc: 'Bảng công, ca làm, timesheet hàng ngày',        icon: 'clock',          color: 'text-cyan-600',     bg: 'bg-cyan-100',     route: '/attendance', new: true },
  { key: 'payroll',     name: 'Bảng lương',          desc: 'Phiếu lương, bảng lương tháng, thu nhập',       icon: 'dollar-sign',    color: 'text-emerald-600',  bg: 'bg-emerald-100',  route: '/payroll', new: true },
  { key: 'expenses',    name: 'Chi phí',             desc: 'Đề nghị thanh toán, hoàn ứng, công tác phí',    icon: 'credit-card',    color: 'text-orange-600',   bg: 'bg-orange-100',   route: '/expenses', new: true },
  { key: 'performance', name: 'Hiệu suất',           desc: 'Đánh giá KPI, review định kỳ, mục tiêu',         icon: 'trending-up',    color: 'text-purple-600',   bg: 'bg-purple-100',   route: '/performance', new: true },
  { key: 'benefits',    name: 'Thuế & Phúc lợi',     desc: 'BHXH, BHYT, thuế TNCN, phúc lợi khác',          icon: 'shield',         color: 'text-pink-600',     bg: 'bg-pink-100',     route: '/benefits', new: true },
  { key: 'seniority',   name: 'Thâm niên',           desc: 'Thâm niên công tác, khen thưởng, kỷ niệm',       icon: 'award',          color: 'text-amber-600',    bg: 'bg-amber-100',    route: '/seniority', new: true },
  { key: 'hr-setup',    name: 'HR Setup',            desc: 'Cấu hình phòng ban, chức vụ, loại nghỉ phép',    icon: 'settings',       color: 'text-gray-600',     bg: 'bg-gray-100',     route: '/hr-setup', new: true },
  { key: 'payroll-cfg', name: 'Cấu hình lương VN',   desc: 'Mức cơ sở, trần BH, giảm trừ, biểu thuế TNCN',   icon: 'sliders',        color: 'text-teal-600',     bg: 'bg-teal-100',     route: '/payroll-config', new: true },
  { key: 'hr-movement', name: 'Biến động nhân sự',   desc: 'Vào/ra, thăng chức, điều chuyển, tỷ lệ nghỉ việc', icon: 'activity',     color: 'text-rose-600',     bg: 'bg-rose-100',     route: '/hr-movement', new: true },
]
</script>
