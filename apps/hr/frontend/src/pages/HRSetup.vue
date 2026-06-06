<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3">
      <Button variant="ghost" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-4 w-4" /></Button>
      <h1 class="text-lg font-semibold text-gray-900 flex-1">HR Setup</h1>
    </header>

    <div v-if="toast" class="fixed top-16 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-sm font-medium" :class="toast.startsWith('✅') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'">{{ toast }}</div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-4xl mx-auto space-y-4">
        <p class="text-xs text-gray-400">Cấu hình danh mục dùng chung cho toàn phân hệ Nhân sự.</p>

        <div v-if="loading" class="flex items-center justify-center py-20"><LoadingIndicator /></div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-for="(sec, key) in data" :key="key" class="rounded-lg border bg-white shadow-sm p-4">
            <div class="flex items-center gap-2 mb-3">
              <FeatherIcon :name="icons[key]" class="h-4 w-4 text-indigo-600" />
              <h3 class="text-sm font-semibold text-gray-700 flex-1">{{ sec.label }}</h3>
              <span class="text-xs text-gray-400">{{ sec.count }}</span>
            </div>

            <!-- Chips -->
            <div class="flex flex-wrap gap-1.5 mb-3 max-h-40 overflow-y-auto">
              <span v-for="item in sec.items" :key="item" class="text-xs bg-gray-100 text-gray-700 rounded-full px-2.5 py-1">{{ shortName(item) }}</span>
              <span v-if="!sec.items.length" class="text-xs text-gray-400">Chưa có mục nào</span>
            </div>

            <!-- Thêm mới -->
            <div class="flex items-center gap-2">
              <input v-model="newItem[key]" @keyup.enter="add(key)" :placeholder="'Thêm ' + sec.label.toLowerCase() + '...'" class="flex-1 text-sm border rounded-lg px-3 py-1.5" />
              <Button size="sm" @click="add(key)" :loading="adding[key]"><FeatherIcon name="plus" class="h-4 w-4" /></Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { frappeRequest, Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'

const data = ref({})
const loading = ref(true)
const toast = ref('')
const newItem = reactive({})
const adding = reactive({})

const icons = {
  department: 'home', designation: 'briefcase', leave_type: 'calendar',
  employment_type: 'file-text', expense_claim_type: 'credit-card',
}

function showToast(msg, ms = 3000) { toast.value = msg; setTimeout(() => toast.value = '', ms) }
function shortName(s) { return (s || '').split(' - ')[0] }

async function load() {
  try { data.value = await frappeRequest({ url: 'hr.api.get_setup_data', method: 'GET', params: {} }) || {} } catch {}
  loading.value = false
}

async function add(key) {
  const name = (newItem[key] || '').trim()
  if (!name) return
  adding[key] = true
  try {
    await frappeRequest({ url: 'hr.api.create_master', method: 'POST', params: { key, name } })
    newItem[key] = ''
    showToast('✅ Đã thêm: ' + name)
    await load()
  } catch (e) { showToast('❌ ' + (e.message || 'Lỗi thêm'), 4000) }
  adding[key] = false
}

onMounted(load)
</script>
