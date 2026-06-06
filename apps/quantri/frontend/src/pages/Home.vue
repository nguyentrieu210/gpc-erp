<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
  <div class="flex items-center gap-2"><FeatherIcon name="shield" class="h-5 w-5 text-purple-600"/><h1 class="text-lg font-bold text-gray-900">Quản trị hệ thống</h1></div>
  <div class="flex items-center gap-3">
    <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4"/><span>Cổng</span></Button>
    <div class="h-4 w-px bg-gray-200"/><span class="text-sm text-gray-600 font-medium">{{ user?.full_name||'Administrator' }}</span>
    <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
  </div>
</header>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
  <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator/></div>
  <div v-else class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <StatCard label="Người dùng" :value="dash.active_users+'/'+dash.total_users" sub="hoạt động/tổng" icon="users" tone="blue" to="/users"/>
      <StatCard label="Vai trò" :value="dash.active_roles+'/'+dash.total_roles" sub="hoạt động/tổng" icon="key" tone="emerald" to="/roles"/>
      <StatCard label="Phân hệ" :value="dash.active_modules+'/'+dash.total_modules" sub="hoạt động/tổng" icon="grid" tone="purple" to="/modules"/>
    </div>
    <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="m in mods" :key="m.key" class="app-card-interactive p-5" @click="$router.push(m.route)">
        <div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg shrink-0" :class="m.bg"><FeatherIcon :name="m.icon" class="h-5 w-5" :class="m.color"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold">{{ m.name }}</h3><p class="text-sm text-gray-500 mt-0.5">{{ m.desc }}</p></div></div>
      </div>
    </div>
  </div>
</main>
</div>
</template>
<script setup>
import { ref } from 'vue'
import { Button,FeatherIcon,LoadingIndicator } from 'frappe-ui'
import { useFrappeApi,StatCard } from '@shared'
const { data:dash,loading }=useFrappeApi('quantri.api.get_dashboard',{initialData:{total_users:0,active_users:0,total_roles:0,active_roles:0,total_modules:0,active_modules:0}})
const { data:user }=useFrappeApi('portal.api.get_current_user')
const loggingOut=ref(false)
const mods=[
  {key:'users',name:'Người dùng',desc:'Quản lý tài khoản',icon:'user-plus',color:'text-blue-600',bg:'bg-blue-100',route:'/users'},
  {key:'roles',name:'Vai trò',desc:'Danh sách role',icon:'key',color:'text-emerald-600',bg:'bg-emerald-100',route:'/roles'},
  {key:'modules',name:'Phân quyền phân hệ',desc:'Module ↔ Role',icon:'grid',color:'text-purple-600',bg:'bg-purple-100',route:'/modules'},
]
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
