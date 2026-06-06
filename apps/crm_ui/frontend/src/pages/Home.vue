<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
      <div class="flex items-center gap-2"><FeatherIcon name="users" class="h-5 w-5 text-indigo-600" /><h1 class="text-lg font-bold text-gray-900">CRM</h1></div>
      <div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4" /><span>Cổng</span></Button>
        <div class="h-4 w-px bg-gray-200" />
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
      </div>
    </header>
    <main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="Lead mới" :value="d?.leads_new ?? 0" icon="user-plus" tone="indigo" to="/leads" />
        <StatCard label="Giá trị cơ hội" :value="fmtShort(d?.opportunities_value)" icon="target" tone="amber" to="/opportunities" />
        <StatCard label="Khách hàng" :value="d?.customers_total ?? 0" icon="users" tone="emerald" to="/customers" />
        <StatCard label="Việc cần làm" :value="d?.open_activities ?? 0" icon="check-square" tone="rose" to="/activities" />
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="app-card p-4">
          <div class="text-sm font-semibold mb-2">Phễu Lead</div>
          <div v-for="f in d?.lead_funnel || []" :key="f.status" class="flex items-center gap-2 py-1 text-sm">
            <span class="w-24 shrink-0 text-gray-600">{{ f.status }}</span>
            <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden"><div class="h-full bg-indigo-500" :style="{ width: barW(f.count) + '%' }" /></div>
            <span class="w-8 text-right font-medium">{{ f.count }}</span>
          </div>
        </div>
        <div class="app-card p-4">
          <div class="flex items-center mb-2"><div class="text-sm font-semibold flex-1">Lead gần đây</div><button class="text-xs text-indigo-600" @click="$router.push('/leads')">Xem tất cả →</button></div>
          <button v-for="l in d?.recent_leads || []" :key="l.name" class="w-full flex items-center gap-2 py-1.5 text-sm border-b last:border-0" @click="$router.push('/leads/' + l.name)">
            <Avatar :name="l.lead_name" :size="26" /><span class="flex-1 text-left truncate">{{ l.lead_name }}</span><StatusBadge :status="l.status_vi" :dot="false" />
          </button>
          <div v-if="!(d?.recent_leads || []).length" class="text-sm text-gray-400">Chưa có lead</div>
        </div>
      </div>
      <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="m in mods" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
          <div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color" /></div><div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div></div>
        </div>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { useFrappeApi, StatCard, StatusBadge, Avatar } from '@shared'
const { data: d } = useFrappeApi('crm_ui.api.get_crm_dashboard', { initialData: {} })
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)
const mods = [
  { key: 'leads', name: 'Lead', desc: 'Tiềm năng → pipeline kéo-thả', icon: 'user-plus', color: 'text-indigo-600', bg: 'bg-indigo-100', route: '/leads' },
  { key: 'opps', name: 'Cơ hội', desc: 'Kanban bán hàng theo giai đoạn', icon: 'target', color: 'text-amber-600', bg: 'bg-amber-100', route: '/opportunities' },
  { key: 'custs', name: 'Khách hàng', desc: 'DS & hồ sơ KH', icon: 'users', color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/customers' },
  { key: 'contacts', name: 'Liên hệ', desc: 'Danh bạ liên hệ', icon: 'phone', color: 'text-cyan-600', bg: 'bg-cyan-100', route: '/contacts' },
  { key: 'acts', name: 'Hoạt động', desc: 'Việc cần làm / theo dõi', icon: 'check-square', color: 'text-rose-600', bg: 'bg-rose-100', route: '/activities' },
  { key: 'camp', name: 'Chiến dịch', desc: 'Marketing campaign', icon: 'flag', color: 'text-violet-600', bg: 'bg-violet-100', route: '/campaigns' },
  { key: 'setup', name: 'Cấu hình', desc: 'Nhóm KH, nguồn lead', icon: 'settings', color: 'text-gray-600', bg: 'bg-gray-100', route: '/setup' },
]
const maxFunnel = computed(() => Math.max(1, ...((d.value?.lead_funnel || []).map((f) => f.count))))
function barW(c) { return Math.max(2, Math.round((Number(c || 0) / maxFunnel.value) * 100)) }
function fmtShort(v) { v = Number(v || 0); if (v >= 1e9) return (v / 1e9).toFixed(1) + ' tỷ'; if (v >= 1e6) return (v / 1e6).toFixed(1) + ' tr'; return v.toLocaleString('vi-VN') }
async function logout() { loggingOut.value = true; try { await fetch('/api/method/portal.api.portal_logout', { method: 'GET', credentials: 'include' }) } catch (e) {} document.cookie.split(';').forEach((c) => { const n = c.split('=')[0].trim(); document.cookie = n + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/' }); window.location.href = '/portal_app/login' }
function goPortal() { window.location.href = '/portal_app' }
</script>
