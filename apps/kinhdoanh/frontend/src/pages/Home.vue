<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center justify-between border-b bg-white px-4 py-3"><div class="flex items-center gap-2"><FeatherIcon name="trending-up" class="h-5 w-5 text-rose-600"/><h1 class="text-lg font-bold text-gray-900">Kinh doanh</h1></div><div class="flex items-center gap-3">
        <Button variant="subtle" @click="goPortal" class="flex items-center gap-1">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          <span>Cổng</span>
        </Button>
        <div class="h-4 w-[1px] bg-gray-200"></div>
        <span class="text-sm text-gray-600 font-medium">{{ user?.full_name || 'Administrator' }}</span>
        <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600 hover:text-red-700">
          Đăng xuất
        </Button>
      </div></header>
<main class="flex-1 p-4 max-w-5xl mx-auto w-full space-y-6">
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3"><div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/sales-orders')"><div class="text-xl font-bold text-rose-600">{{ d?.so_draft??0 }}</div><div class="text-xs text-gray-500">Đơn nháp</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/sales-invoices')"><div class="text-xl font-bold text-red-600">{{ fmtShort(d?.total_receivable) }}</div><div class="text-xs text-gray-500">Phải thu</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/delivery-notes')"><div class="text-xl font-bold text-amber-600">{{ d?.to_deliver??0 }}</div><div class="text-xs text-gray-500">Chờ giao</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/customers')"><div class="text-xl font-bold text-blue-600">{{ d?.customer_count??0 }}</div><div class="text-xs text-gray-500">Khách hàng</div></div></div>
<h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
<div v-for="m in mods" :key="m.key" class="group rounded-xl border bg-white p-5 shadow-sm hover:shadow-md cursor-pointer transition" @click="$router.push(m.route)"><div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div></div></div></div></main></div></template>
<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, frappeRequest, LoadingIndicator } from 'frappe-ui'; import {useFrappeApi} from '../composables/useFrappeApi'
const {data:d}=useFrappeApi('kinhdoanh.api.get_sales_dashboard',{initialData:{}})
const mods=[{key:'cust',name:'Khách hàng',desc:'DS & công nợ KH',icon:'users',color:'text-blue-600',bg:'bg-blue-100',route:'/customers'},{key:'quot',name:'Báo giá',desc:'Gửi báo giá KH',icon:'file-text',color:'text-amber-600',bg:'bg-amber-100',route:'/quotations'},{key:'so',name:'Đơn bán (SO)',desc:'Đơn hàng, tạo giao/HĐ',icon:'shopping-cart',color:'text-rose-600',bg:'bg-rose-100',route:'/sales-orders'},{key:'dn',name:'Xuất giao (DN)',desc:'Giao hàng → kho + GL',icon:'truck',color:'text-emerald-600',bg:'bg-emerald-100',route:'/delivery-notes'},{key:'si',name:'Hóa đơn (SI)',desc:'HĐ bán → 131',icon:'file-plus',color:'text-violet-600',bg:'bg-violet-100',route:'/sales-invoices'},{key:'recv',name:'Phải thu',desc:'Công nợ & thu tiền',icon:'dollar-sign',color:'text-red-600',bg:'bg-red-100',route:'/receivables'},{key:'setup',name:'Cấu hình',desc:'TK, thuế, giá',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/setup'}]
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' tỷ';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';return v.toLocaleString('vi-VN')}
const { data: user } = useFrappeApi('portal.api.get_current_user')
const loggingOut = ref(false)

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

function goPortal() {
  window.location.href = '/portal_app'
}
</script>
