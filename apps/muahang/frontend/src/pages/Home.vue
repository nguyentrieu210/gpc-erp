<template>
<div class="flex flex-col min-h-screen bg-gray-50">
  <header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
    <div class="flex items-center gap-2"><FeatherIcon name="shopping-cart" class="h-5 w-5 text-sky-600" /><h1 class="text-lg font-bold text-gray-900">Mua hàng</h1></div>
    <div class="flex items-center gap-3">
      <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4" /><span>Cổng</span></Button>
      <div class="h-4 w-px bg-gray-200" /><span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
      <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
    </div>
  </header>
  <main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-6">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <StatCard label="PO nháp" :value="d?.po_draft ?? 0" icon="file" tone="sky" to="/purchase-orders" />
      <StatCard label="Chờ nhận hàng" :value="fmtShort(d?.to_receive_value)" icon="truck" tone="amber" to="/purchase-receipts" />
      <StatCard label="HĐ chưa trả" :value="d?.pi_unpaid ?? 0" icon="file-plus" tone="violet" to="/purchase-invoices" />
      <StatCard label="Công nợ phải trả" :value="fmtShort(d?.total_payable)" icon="dollar-sign" tone="rose" to="/payables" />
    </div>
    <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="m in modules" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
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
const { data: d } = useFrappeApi('muahang.api.get_purchase_dashboard', { initialData: {} })
const modules = [
  { key:'sup',name:'Nhà cung cấp',desc:'Danh sách NCC, công nợ, lịch sử GD',icon:'users',color:'text-blue-600',bg:'bg-blue-100',route:'/suppliers' },
  { key:'pr',name:'Đề nghị mua',desc:'Yêu cầu mua hàng, tạo PO',icon:'edit-3',color:'text-amber-600',bg:'bg-amber-100',route:'/purchase-requests' },
  { key:'rfq',name:'Yêu cầu báo giá',desc:'Gửi RFQ → nhận báo giá → PO',icon:'mail',color:'text-sky-600',bg:'bg-sky-100',route:'/rfq' },
  { key:'po',name:'Đơn mua (PO)',desc:'Đặt hàng NCC, in đơn, tạo nhập/HĐ',icon:'file-text',color:'text-indigo-600',bg:'bg-indigo-100',route:'/purchase-orders' },
  { key:'prr',name:'Nhập mua (PR)',desc:'Phiếu nhập mua → vào kho + GL',icon:'truck',color:'text-emerald-600',bg:'bg-emerald-100',route:'/purchase-receipts' },
  { key:'pi',name:'Hóa đơn mua (PI)',desc:'HĐ NCC → công nợ 331 + thuế',icon:'file-plus',color:'text-violet-600',bg:'bg-violet-100',route:'/purchase-invoices' },
  { key:'pay',name:'Công nợ phải trả',desc:'Sổ chi tiết NCC, thanh toán',icon:'dollar-sign',color:'text-rose-600',bg:'bg-rose-100',route:'/payables' },
  { key:'cfg',name:'Cấu hình',desc:'Tài khoản, thuế, nhóm NCC',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/setup' },
]
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' tỷ';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';return v.toLocaleString('vi-VN')}
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
