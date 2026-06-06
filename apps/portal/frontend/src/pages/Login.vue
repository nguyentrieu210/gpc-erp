<template>
  <div class="flex h-screen w-screen items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm rounded-2xl border bg-white p-8 shadow-sm">
      <div class="mb-6 text-center">
        <div
          class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold text-white"
        >
          G
        </div>
        <h1 class="text-xl font-semibold text-gray-900">GPC ERP</h1>
        <p class="mt-1 text-sm text-gray-500">Đăng nhập cổng nội bộ</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <FormControl
          label="Email / Tài khoản"
          v-model="email"
          type="text"
          placeholder="Administrator"
          autocomplete="username"
        />
        <FormControl
          label="Mật khẩu"
          v-model="password"
          type="password"
          placeholder="••••••••"
          autocomplete="current-password"
        />
        <ErrorMessage :message="error" />
        <Button
          variant="solid"
          class="w-full"
          :loading="loading"
          @click="submit"
        >
          Đăng nhập
        </Button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { call } from 'frappe-ui'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!email.value || !password.value) {
    error.value = 'Nhập tài khoản và mật khẩu'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await call('login', { usr: email.value, pwd: password.value })
    // reload đầy đủ để lấy session + boot mới
    window.location.href = '/portal_app'
  } catch (e) {
    error.value = 'Sai tài khoản hoặc mật khẩu'
  } finally {
    loading.value = false
  }
}
</script>
