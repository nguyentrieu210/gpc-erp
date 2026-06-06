<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
      <div class="flex items-center gap-2"><FeatherIcon name="trending-up" class="h-5 w-5 text-rose-600" /><h1 class="text-lg font-bold text-gray-900">Kinh doanh</h1></div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4" /><span>Cổng</span></Button>
        <div class="h-4 w-px bg-gray-200" />
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
      </div>
    </header>

    <main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
      <!-- KPI -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Đơn nháp" :value="d?.so_draft ?? 0" icon="file" tone="amber" to="/sales-orders" />
        <StatCard label="Phải thu" :value="fmtShort(d?.total_receivable)" icon="dollar-sign" tone="rose" sub="công nợ 131" to="/receivables" />
        <StatCard label="Chờ giao" :value="d?.to_deliver ?? 0" icon="truck" tone="emerald" to="/delivery-notes" />
        <StatCard label="Khách hàng" :value="d?.customer_count ?? 0" icon="users" tone="blue" to="/customers" />
      </div>

      <!-- Doanh thu + Top hàng -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="app-card p-4 lg:col-span-2">
          <div class="text-sm font-semibold mb-3">Doanh thu 6 tháng (HĐ đã ghi sổ)</div>
          <div class="flex items-end gap-2 h-40">
            <div v-for="r in d?.revenue_series || []" :key="r.month" class="flex-1 flex flex-col items-center justify-end gap-1">
              <div class="text-[10px] text-gray-500">{{ fmtShort(r.value) }}</div>
              <div class="w-full rounded-t bg-gradient-to-t from-rose-500 to-pink-400" :style="{ height: barH(r.value) + '%' }" />
              <div class="text-[10px] text-gray-400">{{ r.month }}</div>
            </div>
            <div v-if="!(d?.revenue_series || []).length" class="text-sm text-gray-400 self-center mx-auto">Chưa có dữ liệu</div>
          </div>
        </div>
        <div class="app-card p-4">
          <div class="text-sm font-semibold mb-3">Top mặt hàng (90 ngày)</div>
          <div v-if="!(d?.top_items || []).length" class="text-sm text-gray-400">Chưa có dữ liệu</div>
          <div v-for="(t, i) in d?.top_items || []" :key="t.item_code" class="flex items-center gap-2 py-1.5 text-sm border-b last:border-0">
            <span class="w-5 text-center text-xs font-bold text-gray-400">{{ i + 1 }}</span>
            <span class="flex-1 truncate">{{ t.item_name || t.item_code }}</span>
            <span class="font-medium">{{ fmtShort(t.amount) }}</span>
          </div>
        </div>
      </div>

      <!-- Đơn bán gần đây -->
      <div class="app-card p-4">
        <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Đơn bán gần đây</div><button class="text-xs text-indigo-600" @click="$router.push('/sales-orders')">Xem tất cả →</button></div>
        <button v-for="so in d?.recent_so || []" :key="so.name" class="w-full flex items-center gap-2 text-sm px-2 py-2 rounded hover:bg-gray-50 border-b last:border-0" @click="$router.push('/sales-orders/' + so.name)">
          <span class="flex-1 text-left"><span class="font-medium">{{ so.name }}</span> · {{ so.customer_name }}</span>
          <span class="font-semibold">{{ fmtShort(so.grand_total) }}</span>
          <StatusBadge :status="so.status_vi || so.status" :dot="false" />
        </button>
        <div v-if="!(d?.recent_so || []).length" class="text-sm text-gray-400 py-2">Chưa có đơn bán</div>
      </div>

      <!-- Phân hệ -->
      <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="m in mods" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
          <div class="flex items-start gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color" /></div>
            <div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { useFrappeApi, StatCard, StatusBadge } from '@shared'
const { data: d } = useFrappeApi('kinhdoanh.api.get_sales_dashboard', { initialData: {} })
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)
const mods = [
  { key: 'cust', name: 'Khách hàng', desc: 'DS & công nợ KH', icon: 'users', color: 'text-blue-600', bg: 'bg-blue-100', route: '/customers' },
  { key: 'quot', name: 'Báo giá', desc: 'Gửi báo giá KH', icon: 'file-text', color: 'text-amber-600', bg: 'bg-amber-100', route: '/quotations' },
  { key: 'so', name: 'Đơn bán (SO)', desc: 'Đơn hàng, tạo giao/HĐ', icon: 'shopping-cart', color: 'text-rose-600', bg: 'bg-rose-100', route: '/sales-orders' },
  { key: 'dn', name: 'Xuất giao (DN)', desc: 'Giao hàng → kho + GL', icon: 'truck', color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/delivery-notes' },
  { key: 'si', name: 'Hóa đơn (SI)', desc: 'HĐ bán → 131', icon: 'file-plus', color: 'text-violet-600', bg: 'bg-violet-100', route: '/sales-invoices' },
  { key: 'recv', name: 'Phải thu', desc: 'Công nợ & thu tiền', icon: 'dollar-sign', color: 'text-red-600', bg: 'bg-red-100', route: '/receivables' },
  { key: 'setup', name: 'Cấu hình', desc: 'TK, thuế, giá', icon: 'settings', color: 'text-gray-600', bg: 'bg-gray-100', route: '/setup' },
]
const maxRev = computed(() => Math.max(1, ...((d.value?.revenue_series || []).map((r) => r.value))))
function barH(v) { return Math.max(2, Math.round((Number(v || 0) / maxRev.value) * 100)) }
function fmtShort(v) { v = Number(v || 0); if (v >= 1e9) return (v / 1e9).toFixed(1) + ' tỷ'; if (v >= 1e6) return (v / 1e6).toFixed(1) + ' tr'; return v.toLocaleString('vi-VN') }
async function logout() {
  loggingOut.value = true
  try { await fetch('/api/method/portal.api.portal_logout', { method: 'GET', credentials: 'include' }) } catch (e) {}
  document.cookie.split(';').forEach((c) => { const n = c.split('=')[0].trim(); document.cookie = n + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/' })
  window.location.href = '/portal_app/login'
}
function goPortal() { window.location.href = '/portal_app' }
</script>
