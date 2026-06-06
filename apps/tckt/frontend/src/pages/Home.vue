<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
      <div class="flex items-center gap-2"><FeatherIcon name="dollar-sign" class="h-5 w-5 text-green-600" /><h1 class="text-lg font-bold text-gray-900">Tài chính kế toán</h1></div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4" /><span>Cổng</span></Button>
        <div class="h-4 w-px bg-gray-200" />
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
      </div>
    </header>
    <main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Tồn quỹ tiền" :value="fmtShort(d?.cash_balance)" icon="credit-card" tone="emerald" />
        <StatCard label="Phải thu (131)" :value="fmtShort(d?.receivable)" icon="arrow-down-circle" tone="blue" />
        <StatCard label="Phải trả (331)" :value="fmtShort(d?.payable)" icon="arrow-up-circle" tone="rose" />
        <StatCard label="Lợi nhuận tháng" :value="fmtShort(d?.profit_mtd)" icon="trending-up" tone="violet" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="app-card p-4">
          <div class="text-sm font-semibold mb-2">Phát sinh GL theo loại (tháng này)</div>
          <div v-if="!(d?.voucher_breakdown || []).length" class="text-sm text-gray-400">Chưa có phát sinh</div>
          <div v-for="v in d?.voucher_breakdown || []" :key="v.voucher_type" class="flex items-center gap-2 py-1.5 text-sm border-b last:border-0">
            <span class="flex-1 truncate">{{ v.voucher_type }}</span>
            <span class="text-xs text-gray-400">{{ v.voucher_count }} ct</span>
            <span class="font-medium">{{ fmtShort(v.total_debit) }}</span>
          </div>
        </div>
        <div class="app-card p-4">
          <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Bút toán gần đây</div><button class="text-xs text-indigo-600" @click="$router.push('/general-ledger')">Sổ cái →</button></div>
          <div v-for="(g, i) in d?.recent_vouchers || []" :key="i" class="flex items-center gap-2 py-1.5 text-sm border-b last:border-0">
            <span class="flex-1 truncate"><span class="font-medium">{{ g.voucher_no }}</span> · {{ shortAcct(g.account) }}</span>
            <span :class="g.debit > 0 ? 'text-emerald-600' : 'text-rose-600'">{{ fmtShort(g.debit || g.credit) }}</span>
          </div>
          <div v-if="!(d?.recent_vouchers || []).length" class="text-sm text-gray-400">Chưa có bút toán</div>
        </div>
      </div>

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
import { ref } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { useFrappeApi, StatCard } from '@shared'
const { data: d } = useFrappeApi('tckt.api.get_accounting_dashboard', { initialData: {} })
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)
const mods = [
  { key: 'je', name: 'Phiếu kế toán', desc: 'Nhật ký chung, bút toán', icon: 'edit-3', color: 'text-green-600', bg: 'bg-green-100', route: '/journal-entries' },
  { key: 'gl', name: 'Sổ cái (GL)', desc: 'Tra cứu bút toán + drill-down', icon: 'book-open', color: 'text-blue-600', bg: 'bg-blue-100', route: '/general-ledger' },
  { key: 'pe', name: 'Thu / Chi', desc: 'Phiếu thu, phiếu chi', icon: 'repeat', color: 'text-cyan-600', bg: 'bg-cyan-100', route: '/payment-entries' },
  { key: 'tb', name: 'Cân đối TK', desc: 'Bảng cân đối phát sinh', icon: 'layers', color: 'text-amber-600', bg: 'bg-amber-100', route: '/trial-balance' },
  { key: 'coa', name: 'Hệ thống TK', desc: 'Danh mục TK TT200', icon: 'list', color: 'text-violet-600', bg: 'bg-violet-100', route: '/chart-of-accounts' },
  { key: 'pl', name: 'KQKD (P&L)', desc: 'Báo cáo lãi lỗ', icon: 'trending-up', color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/profit-loss' },
  { key: 'bs', name: 'CĐKT (BS)', desc: 'Bảng cân đối kế toán', icon: 'bar-chart-2', color: 'text-indigo-600', bg: 'bg-indigo-100', route: '/balance-sheet' },
  { key: 'cf', name: 'Lưu chuyển tiền', desc: 'Dòng tiền vào/ra', icon: 'activity', color: 'text-teal-600', bg: 'bg-teal-100', route: '/cash-flow' },
  { key: 'bud', name: 'Ngân sách', desc: 'Dự toán & chênh lệch', icon: 'target', color: 'text-orange-600', bg: 'bg-orange-100', route: '/budgets' },
  { key: 'bank', name: 'Đối chiếu NH', desc: 'Đối chiếu ngân hàng', icon: 'check-square', color: 'text-sky-600', bg: 'bg-sky-100', route: '/bank-reconciliation' },
  { key: 'setup', name: 'Cấu hình', desc: 'Năm TC, tiền tệ', icon: 'settings', color: 'text-gray-600', bg: 'bg-gray-100', route: '/setup' },
]
function shortAcct(a) { return (a || '').split(' - ').slice(0, 2).join(' - ') }
function fmtShort(v) { v = Number(v || 0); const s = v < 0 ? '-' : ''; v = Math.abs(v); if (v >= 1e9) return s + (v / 1e9).toFixed(1) + ' tỷ'; if (v >= 1e6) return s + (v / 1e6).toFixed(1) + ' tr'; if (v >= 1e3) return s + (v / 1e3).toFixed(0) + 'k'; return s + v.toLocaleString('vi-VN') }
async function logout() { loggingOut.value = true; try { await fetch('/api/method/portal.api.portal_logout', { method: 'GET', credentials: 'include' }) } catch (e) {} document.cookie.split(';').forEach((c) => { const n = c.split('=')[0].trim(); document.cookie = n + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/' }); window.location.href = '/portal_app/login' }
function goPortal() { window.location.href = '/portal_app' }
</script>
