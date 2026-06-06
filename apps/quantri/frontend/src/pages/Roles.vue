<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.push('/')">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
        </Button>
        <h1 class="text-lg font-semibold text-gray-900">Vai trò</h1>
      </div>
    </header>

    <!-- Search -->
    <div class="border-b bg-white px-4 py-2">
      <input v-model="search" @input="doSearch" placeholder="Tìm vai trò..."
        class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-3 p-4">
      <div class="rounded-lg border bg-white p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">{{ roles.length }}</div>
        <div class="text-xs text-gray-500">Tổng</div>
      </div>
      <div class="rounded-lg border bg-white p-3 text-center">
        <div class="text-2xl font-bold text-green-600">{{ roles.filter(r => !r.disabled).length }}</div>
        <div class="text-xs text-gray-500">Hoạt động</div>
      </div>
      <div class="rounded-lg border bg-white p-3 text-center">
        <div class="text-2xl font-bold text-blue-600">{{ roles.filter(r => r.desk_access).length }}</div>
        <div class="text-xs text-gray-500">Có Desk</div>
      </div>
    </div>

    <!-- List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="!roles.length" class="py-20 text-center text-gray-400">
        <FeatherIcon name="key" class="mx-auto mb-2 h-8 w-8" />
        <p>Không có vai trò nào</p>
      </div>
      <div v-else class="divide-y">
        <div v-for="r in roles" :key="r.name" class="flex items-center px-4 py-3 hover:bg-gray-50">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg mr-3"
            :class="r.disabled ? 'bg-gray-100 text-gray-400' : 'bg-green-100 text-green-600'">
            <FeatherIcon name="key" class="h-4 w-4" />
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900">{{ r.name }}</span>
              <Badge v-if="r.disabled" variant="subtle" theme="red" size="sm">Đã tắt</Badge>
              <Badge v-if="r.desk_access" variant="subtle" theme="blue" size="sm">Desk Access</Badge>
            </div>
            <div class="text-sm text-gray-500">{{ r.user_count || 0 }} người dùng</div>
          </div>
          <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-400" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, FeatherIcon, LoadingIndicator, Badge } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const search = ref('')

const { data: roles, loading, error, fetch: fetchRoles } = useFrappeApi('quantri.api.get_roles', {
  params: { search: '' },
  initialData: [],
})

let timer = null
function doSearch() {
  clearTimeout(timer)
  timer = setTimeout(() => fetchRoles({ search: search.value }), 300)
}
</script>
