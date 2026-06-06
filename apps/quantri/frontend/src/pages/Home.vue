<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <FeatherIcon name="shield" class="h-5 w-5 text-purple-600" />
        <h1 class="text-lg font-semibold text-gray-900">Quản trị hệ thống</h1>
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

    <!-- Dashboard -->
    <main class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator />
      </div>
      <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600">
        {{ error }}
      </div>
      <div v-else class="space-y-6">
        <!-- Stat Cards -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div class="rounded-lg border bg-white p-4 shadow-sm">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                <FeatherIcon name="users" class="h-5 w-5" />
              </div>
              <div>
                <div class="text-2xl font-bold text-gray-900">{{ dash.active_users }}/{{ dash.total_users }}</div>
                <div class="text-sm text-gray-500">Người dùng (hoạt động/tổng)</div>
              </div>
            </div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 text-green-600">
                <FeatherIcon name="key" class="h-5 w-5" />
              </div>
              <div>
                <div class="text-2xl font-bold text-gray-900">{{ dash.active_roles }}/{{ dash.total_roles }}</div>
                <div class="text-sm text-gray-500">Vai trò (hoạt động/tổng)</div>
              </div>
            </div>
          </div>
          <div class="rounded-lg border bg-white p-4 shadow-sm">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
                <FeatherIcon name="grid" class="h-5 w-5" />
              </div>
              <div>
                <div class="text-2xl font-bold text-gray-900">{{ dash.active_modules }}/{{ dash.total_modules }}</div>
                <div class="text-sm text-gray-500">Phân hệ (hoạt động/tổng)</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="border-b px-4 py-3 font-medium text-gray-900">Thao tác nhanh</div>
          <div class="p-4">
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <router-link to="/users" class="flex items-center gap-3 rounded-lg border p-4 hover:shadow-md transition">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                  <FeatherIcon name="user-plus" class="h-5 w-5" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">Người dùng</div>
                  <div class="text-sm text-gray-500">Quản lý tài khoản</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-4 w-4 text-gray-400" />
              </router-link>

              <router-link to="/roles" class="flex items-center gap-3 rounded-lg border p-4 hover:shadow-md transition">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 text-green-600">
                  <FeatherIcon name="key" class="h-5 w-5" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">Vai trò</div>
                  <div class="text-sm text-gray-500">Danh sách role</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-4 w-4 text-gray-400" />
              </router-link>

              <router-link to="/modules" class="flex items-center gap-3 rounded-lg border p-4 hover:shadow-md transition">
                <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
                  <FeatherIcon name="grid" class="h-5 w-5" />
                </div>
                <div>
                  <div class="font-medium text-gray-900">Phân quyền phân hệ</div>
                  <div class="text-sm text-gray-500">Module ↔ Role</div>
                </div>
                <FeatherIcon name="chevron-right" class="ml-auto h-4 w-4 text-gray-400" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, LoadingIndicator, frappeRequest } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const { data: dash, loading, error } = useFrappeApi('quantri.api.get_dashboard', {
  initialData: { total_users: 0, active_users: 0, disabled_users: 0, total_roles: 0, active_roles: 0, total_modules: 0, active_modules: 0 },
})

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
