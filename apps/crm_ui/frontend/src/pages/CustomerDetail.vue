<template>
  <DetailLayout :loading="loading" :title="doc?.customer_name || name" icon="users" icon-class="text-emerald-600" back="/customers"
    :heading="doc?.customer_name" :meta="doc?.customer_group" gradient="from-emerald-600 to-teal-600">
    <div class="app-card p-4">
      <div class="text-sm font-semibold mb-2">Cơ hội liên quan</div>
      <div v-if="!doc?.opportunities?.length" class="text-sm text-gray-400">Chưa có cơ hội</div>
      <button v-for="o in doc?.opportunities || []" :key="o.name" class="w-full flex items-center gap-2 py-2 text-sm border-b last:border-0" @click="$router.push('/opportunities/' + o.name)">
        <span class="flex-1 text-left font-medium">{{ o.title }}</span><span>{{ fmtVnd(o.opportunity_amount) }}</span><StatusBadge :status="o.status" :dot="false" />
      </button>
    </div>
    <template #sidebar>
      <div class="app-card p-4 space-y-1 text-sm">
        <div class="flex justify-between"><span class="text-gray-500">Mã KH</span><span class="font-medium">{{ doc?.name }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Loại</span><span>{{ doc?.customer_type }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">MST</span><span>{{ doc?.tax_id || '—' }}</span></div>
        <div class="flex justify-between"><span class="text-gray-500">Khu vực</span><span>{{ doc?.territory || '—' }}</span></div>
      </div>
    </template>
  </DetailLayout>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { DetailLayout, StatusBadge, callApi, fmtVnd } from '@shared'
const route = useRoute(); const name = route.params.name
const doc = ref(null); const loading = ref(true)
async function load() { loading.value = true; try { doc.value = await callApi('crm_ui.api.get_customer', { name }, 'GET') } finally { loading.value = false } }
load()
</script>
