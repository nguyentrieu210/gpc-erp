<template>
<div class="flex flex-col min-h-screen bg-gray-50">
<header class="flex items-center justify-between border-b bg-white px-4 py-3 sticky top-0 z-20">
  <div class="flex items-center gap-2"><FeatherIcon name="folder" class="h-5 w-5 text-cyan-600"/><h1 class="text-lg font-bold text-gray-900">Dự án</h1></div>
  <div class="flex items-center gap-3">
    <Button variant="subtle" @click="goPortal" class="flex items-center gap-1"><FeatherIcon name="arrow-left" class="h-4 w-4"/><span>Cổng</span></Button>
    <div class="h-4 w-px bg-gray-200"/><span class="text-sm text-gray-600 font-medium">{{ user?.full_name||'Administrator' }}</span>
    <Button variant="subtle" :loading="loggingOut" @click="logout" class="text-red-600">Đăng xuất</Button>
  </div>
</header>
<main class="flex-1 p-4 max-w-6xl mx-auto w-full space-y-6">
  <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator/></div>
  <div v-else class="space-y-6">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <StatCard label="Đang mở" :value="data.active_projects||0" icon="folder" tone="indigo" to="/projects"/>
      <StatCard label="Hoàn thành" :value="data.completed_projects||0" icon="check-circle" tone="emerald"/>
      <StatCard label="Task đang làm" :value="data.open_tasks||0" icon="list" tone="cyan"/>
      <StatCard label="Quá hạn" :value="data.overdue_tasks||0" icon="alert-triangle" :tone="(data.overdue_tasks||0)>0?'rose':'gray'"/>
    </div>
    <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Phân hệ</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="app-card-interactive p-5" @click="$router.push('/projects')">
        <div class="flex items-start gap-3"><div class="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-100 text-cyan-600 shrink-0"><FeatherIcon name="folder" class="h-5 w-5"/></div><div class="flex-1 min-w-0"><h3 class="font-semibold">Tất cả dự án</h3><p class="text-sm text-gray-500 mt-0.5">{{ data.total_projects||0 }} dự án</p></div></div>
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
const { data,loading }=useFrappeApi('duan.api.get_dashboard')
const { data:user }=useFrappeApi('portal.api.get_current_user')
const loggingOut=ref(false)
async function logout(){loggingOut.value=true;try{await fetch('/api/method/portal.api.portal_logout',{method:'GET',credentials:'include'})}catch(e){}document.cookie.split(';').forEach((c)=>{const n=c.split('=')[0].trim();document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'});window.location.href='/portal_app/login'}
function goPortal(){window.location.href='/portal_app'}
</script>
