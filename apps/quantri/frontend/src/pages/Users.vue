<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.push('/')">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
        </Button>
        <h1 class="text-lg font-semibold text-gray-900">Người dùng</h1>
      </div>
      <Button variant="solid" @click="showCreate = true">
        <FeatherIcon name="plus" class="mr-1 h-4 w-4" /> Tạo mới
      </Button>
    </header>

    <!-- Search -->
    <div class="border-b bg-white px-4 py-2">
      <input
        v-model="search"
        @input="doSearch"
        placeholder="Tìm theo email hoặc tên..."
        class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />
    </div>

    <!-- List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator />
      </div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="!users.length" class="py-20 text-center text-gray-400">
        <FeatherIcon name="users" class="mx-auto mb-2 h-8 w-8" />
        <p>Không có người dùng nào</p>
      </div>
      <div v-else class="divide-y">
        <div
          v-for="u in users"
          :key="u.name"
          class="flex items-center px-4 py-3 hover:bg-gray-50 cursor-pointer"
          @click="$router.push('/users/' + u.name)"
        >
          <div class="mr-3 flex h-9 w-9 items-center justify-center rounded-full"
            :class="u.enabled ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'">
            {{ avatarText(u.full_name) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-900 truncate">{{ u.full_name || u.name }}</span>
              <Badge v-if="!u.enabled" variant="subtle" theme="red" size="sm">Đã khóa</Badge>
              <Badge v-if="u.user_type === 'System User'" variant="subtle" theme="blue" size="sm">System</Badge>
            </div>
            <div class="text-sm text-gray-500 truncate">{{ u.name }}</div>
          </div>
          <div class="hidden sm:flex flex-wrap gap-1 mr-2 max-w-[200px]">
            <span
              v-for="r in u.roles?.slice(0, 2)"
              :key="r"
              class="inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
            >{{ r }}</span>
            <span v-if="u.roles?.length > 2" class="text-xs text-gray-400">+{{ u.roles.length - 2 }}</span>
          </div>
          <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-400" />
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showCreate = false">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
        <h2 class="mb-4 text-lg font-semibold">Tạo người dùng mới</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="form.email" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="nguyenvana@example.com" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Họ</label>
              <input v-model="form.last_name" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="Nguyễn" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tên</label>
              <input v-model="form.first_name" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="Văn A" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu (để trống = tự sinh)</label>
            <input v-model="form.password" type="password" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vai trò</label>
            <div class="max-h-32 overflow-y-auto rounded-lg border p-2 space-y-1">
              <label v-for="r in allRoles" :key="r.name" class="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 rounded px-1 py-0.5">
                <input type="checkbox" :value="r.name" v-model="form.roles" class="rounded" />
                {{ r.name }}
              </label>
            </div>
          </div>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="subtle" @click="showCreate = false">Hủy</Button>
          <Button variant="solid" @click="doCreate" :loading="creating">Tạo</Button>
        </div>
        <p v-if="createMsg" class="mt-2 text-sm" :class="createErr ? 'text-red-500' : 'text-green-600'">{{ createMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator, Badge } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const search = ref('')
const showCreate = ref(false)
const creating = ref(false)
const createMsg = ref('')
const createErr = ref(false)
const form = ref({ email: '', first_name: '', last_name: '', password: '', roles: [] })

const { data: allRoles } = useFrappeApi('quantri.api.get_roles', { initialData: [] })

const { data: users, loading, error, fetch: fetchUsers } = useFrappeApi('quantri.api.get_users', {
  params: { search: '', page: 1, page_length: 50 },
  initialData: [],
})

let searchTimer = null
function doSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchUsers({ search: search.value, page: 1, page_length: 50 })
  }, 300)
}

async function doCreate() {
  if (!form.value.email || !form.value.first_name) {
    createMsg.value = 'Email và Tên không được để trống.'
    createErr.value = true
    return
  }
  creating.value = true
  createMsg.value = ''
  createErr.value = false
  try {
    const data = await frappeRequest({ url: 'quantri.api.create_user', method: 'POST', params: { ...form.value } })
    createMsg.value = data.msg || data
    createErr.value = data.exc_type ? true : false
    if (!createErr.value) {
      setTimeout(() => { showCreate.value = false; createMsg.value = ''; fetchUsers() }, 800)
    }
  } catch (e) {
    createMsg.value = 'Lỗi kết nối'
    createErr.value = true
  } finally {
    creating.value = false
  }
}

function avatarText(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[parts.length - 2][0] + parts[parts.length - 1][0]).toUpperCase()
  return parts[0].slice(0, 2).toUpperCase()
}
</script>
