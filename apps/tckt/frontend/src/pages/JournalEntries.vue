<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="edit-3" class="h-5 w-5 text-green-600"/><h1 class="text-lg font-bold flex-1">Phiếu kế toán</h1><Button variant="solid" theme="green" @click="openCreate">+ Tạo phiếu</Button></header>
<main class="flex-1 p-4 max-w-4xl mx-auto"><div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="py-10 text-center text-gray-400">Chưa có phiếu</div>
<div v-for="je in rows" :key="je.name" class="flex items-center px-4 py-3"><div class="flex-1"><div class="font-medium">{{ je.name }} <span :class="je.docstatus===1?'text-emerald-600':'text-amber-600'">{{ je.docstatus===1?'Đã ghi':'Nháp' }}</span></div><div class="text-xs text-gray-500">{{ $fmtDate(je.posting_date) }} · {{ je.user_remark||'' }}</div></div>
<div class="text-right"><div class="text-sm">Nợ {{ fmtVnd(je.total_debit) }}</div><div class="text-xs text-gray-400">Có {{ fmtVnd(je.total_credit) }}</div></div></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-2xl p-5 max-h-[92vh] overflow-y-auto"><h3 class="font-semibold mb-4">Bút toán mới</h3>
<label class="block mb-3"><span class="text-sm text-gray-600">Ngày</span><input type="date" v-model="f.posting_date" class="inp"/></label>
<label class="block mb-3"><span class="text-sm text-gray-600">Diễn giải</span><input v-model="f.remark" class="inp"/></label>
<div class="border rounded-lg mb-3"><div class="grid grid-cols-12 gap-1 bg-gray-50 px-2 py-1.5 text-xs"><div class="col-span-5">Tài khoản</div><div class="col-span-3 text-right">Nợ</div><div class="col-span-3 text-right">Có</div><div class="col-span-1"></div></div>
<div v-for="(a,i) in f.accounts" :key="i" class="grid grid-cols-12 gap-1 px-2 py-1.5 items-center border-t">
<select v-model="a.account" class="col-span-5 inp !py-1 !text-xs"><option value="">— TK —</option><option v-for="ac in accts" :key="ac.name" :value="ac.name">{{ ac.account_number }} {{ ac.account_name }}</option></select>
<input v-model.number="a.debit" type="number" class="col-span-3 inp !py-1 text-right"/><input v-model.number="a.credit" type="number" class="col-span-3 inp !py-1 text-right"/>
<button class="col-span-1 text-red-500 text-xs" @click="f.accounts.splice(i,1)">×</button></div></div>
<Button variant="subtle" size="sm" @click="f.accounts.push({account:'',debit:0,credit:0})">+ Dòng</Button>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" theme="green" :loading="saving" @click="save">Ghi sổ</Button></div></div></div></div></template>
<script setup>
import {ref,reactive} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {useFrappeApi,callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false)
const {data:coa}=useFrappeApi('tckt.api.get_chart_of_accounts',{initialData:{accounts:[]}})
const accts=ref([])
async function reload(){loading.value=true;try{rows.value=(await callApi('tckt.api.get_journal_entries',{},'GET'))?.entries||[];accts.value=(await callApi('tckt.api.get_chart_of_accounts',{},'GET'))?.accounts||[]}finally{loading.value=false}};reload()
const show=ref(false),saving=ref(false);const f=reactive({posting_date:new Date().toISOString().slice(0,10),remark:'',accounts:[{account:'',debit:0,credit:0}]})
function openCreate(){f.posting_date=new Date().toISOString().slice(0,10);f.remark='';f.accounts=[{account:'',debit:0,credit:0}];show.value=true}
async function save(){const acs=f.accounts.filter(a=>a.account&&(a.debit>0||a.credit>0));if(!acs.length||!f.remark){alert('Nhập diễn giải + ít nhất 1 dòng');return};saving.value=true;try{await callApi('tckt.api.create_journal_entry',{accounts:JSON.stringify(acs),posting_date:f.posting_date,remark:f.remark,submit:1});show.value=false;reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
function fmtVnd(v){return Number(v||0).toLocaleString('vi-VN')+' ₫'}
</script>
