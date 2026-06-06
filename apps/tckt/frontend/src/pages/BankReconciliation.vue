<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="credit-card" class="h-5 w-5 text-teal-600"/><h1 class="text-lg font-bold text-gray-900 flex-1">Đối chiếu ngân hàng</h1></header>
<main class="flex-1 p-4 max-w-4xl mx-auto space-y-4">
<div class="bg-white rounded-xl border p-4">
<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
<label class="block"><span class="text-sm text-gray-600 block mb-1">TK Ngân hàng</span>
<select v-model="bankAcct" @change="reload" class="inp"><option value="">— chọn TK —</option><option v-for="b in bankAccounts" :key="b.name" :value="b.name">{{ b.account_name }} ({{ b.bank_account_no }})</option></select></label>
<input type="date" v-model="fd" @change="reload" class="inp self-end"/>
<input type="date" v-model="td" @change="reload" class="inp self-end"/>
</div>

<div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<template v-else-if="bankAcct">
<div class="flex justify-between mb-3 text-sm"><span>{{ items.length }} giao dịch chưa đối chiếu</span><span class="font-bold text-amber-600">Tổng: {{ fmtVnd(totalUncleared) }}</span></div>
<div class="rounded-lg border overflow-hidden"><table class="w-full text-sm"><thead><tr class="bg-gray-50 text-xs text-gray-500"><th class="px-2 py-1.5"><input type="checkbox" v-model="selectAll" @change="toggleAll"/></th><th>Ngày</th><th>Chứng từ</th><th>Nội dung</th><th class="text-right">Số tiền</th></tr></thead>
<tbody><tr v-if="!items.length"><td colspan="5" class="py-8 text-center text-gray-400">Không có giao dịch chưa đối chiếu</td></tr>
<tr v-for="it in items" :key="it.name" class="border-t"><td class="px-2"><input type="checkbox" v-model="it._sel"/></td><td class="py-1.5">{{ $fmtDate(it.posting_date) }}</td><td class="text-xs">{{ it.name }}</td><td class="text-xs text-gray-500">{{ it.party||it.ref_no }}</td><td class="text-right font-medium">{{ fmtVnd(it.amount) }}</td></tr></tbody></table></div>
<Button v-if="selected.length" variant="solid" theme="teal" :loading="saving" @click="doClearance" class="mt-3">Đối chiếu {{ selected.length }} giao dịch ({{ fmtVnd(selTotal) }})</Button>
</template>
<div v-else class="py-10 text-center text-gray-400">Chọn tài khoản ngân hàng để bắt đầu.</div>
</div>

<!-- History -->
<div class="bg-white rounded-xl border p-4"><h3 class="font-medium mb-3 text-gray-700">Lịch sử đối chiếu</h3>
<div v-if="!history.length" class="py-4 text-center text-gray-400 text-sm">Chưa có phiếu đối chiếu</div>
<div v-for="h in history" :key="h.name" class="flex items-center py-2 border-t text-sm"><div class="flex-1">{{ h.name }} · {{ $fmtDate(h.from_date) }} → {{ $fmtDate(h.to_date) }}</div></div></div>
</main></div></template>

<script setup>
import {ref,computed} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const {data:bankAccounts}=useFrappeApi('tckt.api.get_bank_accounts',{initialData:[]})
const items=ref([]),loading=ref(false),history=ref([]),saving=ref(false)
const bankAcct=ref(''),fd=ref('2026-01-01'),td=ref(new Date().toISOString().slice(0,10)),selectAll=ref(false)

async function reload(){
  loading.value=true; items.value=[]; history.value=[]
  try{
    if(bankAcct.value){
      const r=await callApi('tckt.api.get_bank_clearance',{bank_account:bankAcct.value,from_date:fd.value,to_date:td.value},'GET')
      items.value=(r?.items||[]).map(it=>({...it,_sel:false}))
    }
    const h=await callApi('tckt.api.get_bank_clearance_history',{bank_account:bankAcct.value},'GET')
    history.value=h?.entries||[]
  }finally{loading.value=false}
}
reload()

const selected=computed(()=>items.value.filter(it=>it._sel))
const selTotal=computed(()=>selected.value.reduce((s,it)=>s+(Number(it.amount)||0),0))
const totalUncleared=computed(()=>items.value.reduce((s,it)=>s+(Number(it.amount)||0),0))
function toggleAll(){items.value.forEach(it=>it._sel=selectAll.value)}
async function doClearance(){
  saving.value=true
  try{
    await callApi('tckt.api.submit_bank_clearance',{bank_account:bankAcct.value,from_date:fd.value,to_date:td.value,entries:JSON.stringify(selected.value)})
    await reload(); alert('Đã đối chiếu thành công')
  }catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}
}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
