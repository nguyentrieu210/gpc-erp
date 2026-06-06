<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Hệ thống tài khoản (TT200)" icon="list" icon-class="text-violet-600" />
    <main class="flex-1 p-4 max-w-4xl mx-auto w-full space-y-3">
      <div class="flex flex-wrap gap-1">
        <button class="text-xs px-3 py-1.5 rounded-full" :class="!rt ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="rt = ''">Tất cả</button>
        <button v-for="t in rts" :key="t.k" class="text-xs px-3 py-1.5 rounded-full" :class="rt === t.k ? 'bg-indigo-600 text-white' : 'bg-gray-100'" @click="rt = t.k">{{ t.label }}</button>
      </div>
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <div v-else class="space-y-3">
        <div v-for="grp in grouped" :key="grp.k" class="app-card overflow-hidden">
          <div class="px-4 py-2 bg-gray-50 font-semibold text-sm flex items-center gap-2"><span class="w-2 h-2 rounded-full" :class="grp.dot" />{{ grp.label }} <span class="text-xs text-gray-400">({{ grp.rows.length }})</span></div>
          <div class="divide-y">
            <div v-for="a in grp.rows" :key="a.name" class="flex items-center px-4 py-2 text-sm">
              <span class="w-16 text-gray-500 font-mono text-xs">{{ a.account_number || '' }}</span>
              <span class="flex-1">{{ a.account_name }}</span>
              <span class="text-xs text-gray-400">{{ a.account_type || '' }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import { PageHeader, callApi } from '@shared'
const all = ref([]); const loading = ref(false); const rt = ref('')
const rts = [
  { k: 'Asset', label: 'Tài sản' }, { k: 'Liability', label: 'Nợ phải trả' }, { k: 'Equity', label: 'Vốn CSH' },
  { k: 'Income', label: 'Doanh thu' }, { k: 'Expense', label: 'Chi phí' },
]
const DOT = { Asset: 'bg-blue-500', Liability: 'bg-amber-500', Equity: 'bg-violet-500', Income: 'bg-emerald-500', Expense: 'bg-rose-500' }
async function reload() { loading.value = true; try { all.value = (await callApi('tckt.api.get_chart_of_accounts', {}, 'GET'))?.accounts || [] } finally { loading.value = false } }
reload()
const grouped = computed(() => rts.filter((t) => !rt.value || rt.value === t.k).map((t) => ({
  k: t.k, label: t.label, dot: DOT[t.k],
  rows: all.value.filter((a) => a.root_type === t.k).sort((a, b) => String(a.account_number || '').localeCompare(String(b.account_number || ''))),
})).filter((g) => g.rows.length))
</script>
