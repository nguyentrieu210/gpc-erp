<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <FeatherIcon name="folder" class="h-5 w-5 text-cyan-600" />
        <h1 class="text-lg font-semibold text-gray-900">Dự án</h1>
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
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else class="space-y-4">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-2xl font-bold text-gray-900">{{ data.active_projects || 0 }}</div>
            <div class="text-xs text-gray-500">Đang mở</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-2xl font-bold text-green-600">{{ data.completed_projects || 0 }}</div>
            <div class="text-xs text-gray-500">Hoàn thành</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-2xl font-bold text-cyan-600">{{ data.open_tasks || 0 }}</div>
            <div class="text-xs text-gray-500">Task đang làm</div>
          </div>
          <div class="rounded-lg border bg-white p-3 text-center shadow-sm">
            <div class="text-2xl font-bold" :class="(data.overdue_tasks || 0) > 0 ? 'text-red-600' : 'text-gray-400'">{{ data.overdue_tasks || 0 }}</div>
            <div class="text-xs text-gray-500">Quá hạn</div>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <router-link to="/projects" class="flex items-center gap-3 rounded-lg border bg-white p-4 shadow-sm hover:shadow-md transition">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-100 text-cyan-600"><FeatherIcon name="folder" class="h-5 w-5" /></div>
            <div class="flex-1"><div class="font-medium text-gray-900">Tất cả dự án</div><div class="text-sm text-gray-500">{{ data.total_projects || 0 }} dự án</div></div>
            <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-400" />
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, LoadingIndicator, frappeRequest } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const { data, loading, error } = useFrappeApi('duan.api.get_dashboard')

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
