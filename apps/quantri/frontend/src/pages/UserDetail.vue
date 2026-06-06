<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="flex items-center justify-between border-b bg-white px-4 py-3">
      <div class="flex items-center gap-2">
        <Button variant="ghost" @click="$router.push('/users')">
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
        </Button>
        <h1 class="text-lg font-semibold text-gray-900">{{ user?.full_name || 'Chi tiết người dùng' }}</h1>
      </div>
      <Button v-if="user" variant="solid" :loading="saving" @click="doSave">Lưu</Button>
    </header>

    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <LoadingIndicator />
      </div>
      <div v-else-if="error" class="p-4 text-red-500">{{ error }}</div>
      <div v-else-if="user" class="max-w-2xl mx-auto space-y-6">

        <!-- Thông tin cơ bản -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="border-b px-4 py-3 font-medium text-gray-900">Thông tin cơ bản</div>
          <div class="p-4 space-y-3">
            <div class="flex items-center gap-4">
              <div class="flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold"
                :class="user.enabled ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'">
                {{ avatarText(user.full_name) }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-lg font-medium">{{ user.full_name }}</span>
                  <Badge v-if="user.enabled" variant="subtle" theme="green" size="sm">Hoạt động</Badge>
                  <Badge v-else variant="subtle" theme="red" size="sm">Đã khóa</Badge>
                </div>
                <div class="text-sm text-gray-500">{{ user.email }}</div>
                <div class="text-xs text-gray-400">Tạo: {{ fmtDate(user.creation) }}</div>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Họ</label>
                <input v-model="edit.last_name" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tên</label>
                <input v-model="edit.first_name" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" v-model="edit.email" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">SĐT</label>
                <input v-model="edit.mobile_no" class="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
              </div>
            </div>

            <div>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="edit.enabled" class="rounded" />
                <span class="text-sm text-gray-700">Kích hoạt tài khoản</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Roles -->
        <div class="rounded-lg border bg-white shadow-sm">
          <div class="border-b px-4 py-3 font-medium text-gray-900">Vai trò (Roles)</div>
          <div class="p-4">
            <div class="max-h-60 overflow-y-auto space-y-1">
              <label v-for="r in allRoles" :key="r.name" class="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 rounded px-2 py-1.5">
                <input type="checkbox" :value="r.name" v-model="edit.roles" class="rounded" />
                <span class="flex-1">{{ r.name }}</span>
                <Badge v-if="r.disabled" variant="subtle" theme="red" size="sm">Tắt</Badge>
                <Badge v-else-if="r.desk_access" variant="subtle" theme="blue" size="sm">Desk</Badge>
              </label>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="rounded-lg border border-red-200 bg-red-50 p-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-red-800">Vô hiệu hóa tài khoản</div>
              <div class="text-sm text-red-600">User sẽ không thể đăng nhập</div>
            </div>
            <Button v-if="user.enabled" variant="solid" theme="red" @click="doDisable" :loading="disabling">
              Khóa
            </Button>
            <Button v-else variant="subtle" theme="green" @click="doEnable">
              Mở khóa
            </Button>
          </div>
        </div>

        <!-- Save message -->
        <p v-if="saveMsg" class="text-sm rounded-lg p-3" :class="saveErr ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">{{ saveMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator, Badge } from 'frappe-ui'
import { useFrappeApi } from '../composables/useFrappeApi'

const route = useRoute()
const router = useRouter()
const saving = ref(false)
const disabling = ref(false)
const saveMsg = ref('')
const saveErr = ref(false)
const edit = ref({})

const userId = route.params.id

const { data: user, loading, error } = useFrappeApi('quantri.api.get_user_detail', {
  params: { user: userId },
  onSuccess(d) {
    edit.value = {
      first_name: d.first_name || '',
      last_name: d.last_name || '',
      email: d.email || '',
      mobile_no: d.mobile_no || '',
      enabled: d.enabled,
      roles: (d.roles || []).map(r => r.role),
    }
  },
})

const { data: allRoles } = useFrappeApi('quantri.api.get_roles', { initialData: [] })

async function doSave() {
  saving.value = true
  saveMsg.value = ''
  try {
    const d = await frappeRequest({ url: 'quantri.api.update_user', method: 'POST', params: { user: userId, ...edit.value } })
    saveMsg.value = d?.msg || d || 'Đã lưu'
    saveErr.value = !!d?.exc_type
  } catch (e) {
    saveMsg.value = 'Lỗi kết nối'
    saveErr.value = true
  } finally { saving.value = false }
}

async function doDisable() {
  disabling.value = true
  await frappeRequest({ url: 'quantri.api.disable_user', method: 'POST', params: { user: userId } })
  edit.value.enabled = false
  disabling.value = false
}

async function doEnable() {
  edit.value.enabled = true
  await doSave()
}

function avatarText(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[parts.length - 2][0] + parts[parts.length - 1][0]).toUpperCase()
  return parts[0].slice(0, 2).toUpperCase()
}

function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('vi-VN')
}
</script>
