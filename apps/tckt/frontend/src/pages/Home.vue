<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center justify-between border-b bg-white px-4 py-3"><div class="flex items-center gap-2"><FeatherIcon name="dollar-sign" class="h-5 w-5 text-green-600"/><h1 class="text-lg font-bold text-gray-900">Tài chính</h1></div><div class="flex items-center gap-3">
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
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3"><div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/journal-entries')"><div class="text-xl font-bold text-green-600">{{ d?.je_count??0 }}</div><div class="text-xs text-gray-500">Phiếu kế toán</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/general-ledger')"><div class="text-xl font-bold text-blue-600">{{ fmtShort(d?.gl_count) }}</div><div class="text-xs text-gray-500">Bút toán GL</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm cursor-pointer" @click="$router.push('/chart-of-accounts')"><div class="text-xl font-bold text-violet-600">{{ d?.account_count??0 }}</div><div class="text-xs text-gray-500">Tài khoản</div></div>
<div class="rounded-xl border bg-white p-3 text-center shadow-sm"><div class="text-xl font-bold text-emerald-600">{{ fmtShort(d?.revenue_mtd) }}</div><div class="text-xs text-gray-500">Doanh thu tháng</div></div></div>
<h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
<div v-for="m in mods" :key="m.key" class="group rounded-xl border bg-white p-5 shadow-sm hover:shadow-md cursor-pointer transition" @click="$router.push(m.route)"><div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div></div></div></div></main></div></template>
<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, frappeRequest, LoadingIndicator } from 'frappe-ui'; import {useFrappeApi} from '../composables/useFrappeApi'
const {data:d}=useFrappeApi('tckt.api.get_accounting_dashboard',{initialData:{}})
const mods=[{key:'je',name:'Phiếu kế toán',desc:'Nhật ký chung, bút toán',icon:'edit-3',color:'text-green-600',bg:'bg-green-100',route:'/journal-entries'},{key:'gl',name:'Sổ cái (GL)',desc:'Tra cứu bút toán',icon:'book-open',color:'text-blue-600',bg:'bg-blue-100',route:'/general-ledger'},{key:'tb',name:'Cân đối TK',desc:'Bảng cân đối phát sinh',icon:'layers',color:'text-amber-600',bg:'bg-amber-100',route:'/trial-balance'},{key:'coa',name:'Hệ thống TK',desc:'Danh mục tài khoản TT200',icon:'list',color:'text-violet-600',bg:'bg-violet-100',route:'/chart-of-accounts'},{key:'pl',name:'KQKD (P&L)',desc:'Báo cáo lãi lỗ',icon:'trending-up',color:'text-emerald-600',bg:'bg-emerald-100',route:'/profit-loss'},{key:'bs',name:'CĐKT (BS)',desc:'Bảng cân đối kế toán',icon:'bar-chart-2',color:'text-indigo-600',bg:'bg-indigo-100',route:'/balance-sheet'},{key:'setup',name:'Cấu hình',desc:'Năm TC, tiền tệ',icon:'settings',color:'text-gray-600',bg:'bg-gray-100',route:'/setup'}]
function fmtShort(v){v=Number(v||0);if(v>=1e9)return (v/1e9).toFixed(1)+' tỷ';if(v>=1e6)return (v/1e6).toFixed(1)+' tr';if(v>=1e3)return (v/1e3).toFixed(0)+'k';return v.toLocaleString('vi-VN')}
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
