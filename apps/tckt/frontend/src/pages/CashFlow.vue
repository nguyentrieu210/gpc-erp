<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader title="Lưu chuyển tiền tệ" icon="activity" icon-class="text-teal-600" />
    <main class="flex-1 p-4 max-w-4xl mx-auto w-full space-y-3">
      <div class="flex gap-2 items-end">
        <div><label class="text-xs text-gray-500">Từ ngày</label><input type="date" v-model="fd" @change="reload" class="inp" /></div>
        <div><label class="text-xs text-gray-500">Đến ngày</label><input type="date" v-model="td" @change="reload" class="inp" /></div>
      </div>
      <div v-if="loading" class="py-10 text-center"><LoadingIndicator /></div>
      <template v-else>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Tồn đầu kỳ" :value="fmtShort(d.opening)" icon="circle" tone="blue" />
          <StatCard label="Tiền vào" :value="fmtShort(d.inflow)" icon="arrow-down-circle" tone="emerald" />
          <StatCard label="Tiền ra" :value="fmtShort(d.outflow)" icon="arrow-up-circle" tone="rose" />
          <StatCard label="Tồn cuối kỳ" :value="fmtShort(d.closing)" icon="circle" tone="violet" />
        </div>
        <div class="app-card p-4">
          <div class="text-sm font-semibold mb-2">Dòng tiền theo nguồn</div>
          <table class="w-full text-sm">
            <thead><tr><th class="px-2 py-1 text-left">Nguồn</th><th class="px-2 py-1 text-right">Tiền vào</th><th class="px-2 py-1 text-right">Tiền ra</th><th class="px-2 py-1 text-right">Ròng</th></tr></thead>
            <tbody>
              <tr v-for="r in d.rows || []" :key="r.group"><td class="px-2 py-1.5">{{ r.group }}</td><td class="px-2 py-1.5 text-right text-emerald-600">{{ money(r.inflow) }}</td><td class="px-2 py-1.5 text-right text-rose-600">{{ money(r.outflow) }}</td><td class="px-2 py-1.5 text-right font-medium" :class="r.net >= 0 ? 'text-emerald-700' : 'text-rose-700'">{{ money(r.net) }}</td></tr>
              <tr v-if="!(d.rows || []).length"><td colspan="4" class="py-4 text-center text-gray-400">Chưa có dòng tiền</td></tr>
              <tr class="bg-gray-50 font-semibold"><td class="px-2 py-2">Ròng trong kỳ</td><td class="px-2 py-2 text-right text-emerald-600">{{ money(d.inflow) }}</td><td class="px-2 py-2 text-right text-rose-600">{{ money(d.outflow) }}</td><td class="px-2 py-2 text-right">{{ money(d.net) }}</td></tr>
            </tbody>
          </table>
        </div>
      </template>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import { PageHeader, StatCard, callApi, money } from '@shared'
const d = ref({}); const loading = ref(false); const fd = ref('2026-01-01'); const td = ref(new Date().toISOString().slice(0, 10))
async function reload() { loading.value = true; try { d.value = await callApi('tckt.api.get_cash_flow', { from_date: fd.value, to_date: td.value }, 'GET') } finally { loading.value = false } }
reload()
function fmtShort(v) { v = Number(v || 0); const s = v < 0 ? '-' : ''; v = Math.abs(v); if (v >= 1e9) return s + (v / 1e9).toFixed(1) + ' tỷ'; if (v >= 1e6) return s + (v / 1e6).toFixed(1) + ' tr'; if (v >= 1e3) return s + (v / 1e3).toFixed(0) + 'k'; return s + v.toLocaleString('vi-VN') }
</script>
