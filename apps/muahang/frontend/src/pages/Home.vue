<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-10">
      <div class="flex items-center gap-2">
        <FeatherIcon name="shopping-cart" class="h-5 w-5 text-sky-600" />
        <h1 class="text-lg font-bold text-gray-900">Mua hàng</h1>
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
    <main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-6">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer hover:shadow-md" @click="$router.push('/purchase-orders')">
          <div class="text-xl font-bold text-sky-600">{{ d?.po_draft ?? 0 }}</div><div class="text-xs text-gray-500">PO nháp</div>
        </div>
        <div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer hover:shadow-md" @click="$router.push('/purchase-receipts')">
          <div class="text-xl font-bold text-amber-600">{{ fmtShort(d?.to_receive_value) }}</div><div class="text-xs text-gray-500">Chờ nhận hàng</div>
        </div>
        <div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer hover:shadow-md" @click="$router.push('/purchase-invoices')">
          <div class="text-xl font-bold text-violet-600">{{ d?.pi_unpaid ?? 0 }}</div><div class="text-xs text-gray-500">HĐ chưa trả</div>
        </div>
        <div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer hover:shadow-md" @click="$router.push('/payables')">
          <div class="text-xl font-bold" :class="(d?.total_payable) ? 'text-red-600' : 'text-gray-400'">{{ fmtShort(d?.total_payable) }}</div>
          <div class="text-xs text-gray-500">Công nợ phải trả</div>
        </div>
      </div>
      <div v-if="setup && !setup.ready" class="rounded-lg border border-amber-300 bg-amber-50 p-4 flex items-start gap-3">
        <FeatherIcon name="alert-triangle" class="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
        <div class="flex-1 text-sm text-amber-800"><div class="font-medium">Chưa cấu hình đầy đủ</div><div>Cần tài khoản phải trả + chi phí mặc định.</div></div>
        <Button variant="solid" theme="sky" @click="$router.push('/setup')">Cấu hình</Button>
      </div>
      <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">Phân hệ</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="m in modules" :key="m.key" class="group rounded-xl border bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md cursor-pointer" @click="$router.push(m.route)">
          <div class="flex items-start gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color" /></div>
            <div class="flex-1 min-w-0"><h3 class="font-semibold text-gray-900 group-hover:text-sky-600 transition">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, frappeRequest, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'
const { data: d } = useFrappeApi('muahang.api.get_purchase_dashboard', { initialData: {} })
const { data: setup } = useFrappeApi('muahang.api.get_muahang_setup_status', { initialData: null })
const modules = [
  { key: 'sup', name: 'Nhà cung cấp', desc: 'Danh sách NCC, công nợ, lịch sử GD', icon: 'users', color: 'text-blue-600', bg: 'bg-blue-100', route: '/suppliers' },
  { key: 'pr', name: 'Đề nghị mua', desc: 'Yêu cầu mua hàng, tạo PO', icon: 'edit-3', color: 'text-amber-600', bg: 'bg-amber-100', route: '/purchase-requests' },
  { key: 'po', name: 'Đơn mua (PO)', desc: 'Đặt hàng NCC, in đơn, tạo nhập/hóa đơn', icon: 'file-text', color: 'text-sky-600', bg: 'bg-sky-100', route: '/purchase-orders' },
  { key: 'prr', name: 'Nhập mua (PR)', desc: 'Phiếu nhập mua → vào kho + GL', icon: 'truck', color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/purchase-receipts' },
  { key: 'pi', name: 'Hóa đơn mua (PI)', desc: 'Hóa đơn NCC → công nợ 331 + thuế GTGT', icon: 'file-plus', color: 'text-violet-600', bg: 'bg-violet-100', route: '/purchase-invoices' },
  { key: 'pay', name: 'Công nợ phải trả', desc: 'Sổ chi tiết NCC, thanh toán', icon: 'dollar-sign', color: 'text-rose-600', bg: 'bg-rose-100', route: '/payables' },
  { key: 'cfg', name: 'Cấu hình', desc: 'Tài khoản, thuế, nhóm NCC', icon: 'settings', color: 'text-gray-600', bg: 'bg-gray-100', route: '/setup' },
]
function fmtShort(v) { v = Number(v || 0); if (v >= 1e9) return (v / 1e9).toFixed(1) + ' tỷ'; if (v >= 1e6) return (v / 1e6).toFixed(1) + ' tr'; return v.toLocaleString('vi-VN') }
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)

async function logout() {
  loggingOut.value = true
  try {
    await frappeRequest({ url: 'logout', method: 'POST' })
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

function goPortal() {
  window.location.href = '/portal_app'
}
</script>
