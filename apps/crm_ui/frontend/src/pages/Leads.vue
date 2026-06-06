<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0"><button class="text-gray-500" @click="$router.push('/')"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="user-plus" class="h-5 w-5 text-indigo-600"/><h1 class="text-lg font-bold flex-1">Lead</h1><Button variant="solid" @click="openCreate">+ Thêm</Button></header>
<main class="flex-1 p-4 max-w-5xl mx-auto"><div class="flex gap-2 mb-3 overflow-x-auto">
<button v-for="s in statuses" :key="s.value" class="px-3 py-1.5 rounded-full text-sm border whitespace-nowrap" :class="st===s.value?'bg-indigo-600 text-white border-indigo-600':'bg-white'" @click="st=s.value;reload()">{{ s.label }}</button></div>
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"><div v-if="loading" class="col-span-full py-10 text-center"><LoadingIndicator/></div>
<div v-else-if="!rows.length" class="col-span-full py-10 text-center text-gray-400">Chưa có lead</div>
<div v-for="l in rows" :key="l.name" class="rounded-xl border bg-white p-4 shadow-sm">
<div class="flex justify-between"><div class="font-semibold">{{ l.lead_name }}</div><span class="text-xs px-2 py-0.5 rounded-full" :class="badge(l.status)">{{ l.status_vi }}</span></div>
<div class="text-xs text-gray-500 mt-1">{{ l.company_name||'' }} · {{ l.email_id||'' }} · {{ l.mobile_no||'' }}</div>
<div class="flex gap-2 mt-3"><select v-model="l._ns" @change="move(l)" class="inp !py-1 text-xs"><option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option></select>
<Button variant="solid" size="sm" @click="convert(l)">→ Opp</Button></div></div></div>
</main>
<div v-if="show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="show=false"><div class="bg-white rounded-xl w-full max-w-sm p-5"><h3 class="font-semibold mb-4">Thêm Lead</h3>
<label class="block mb-2"><span class="text-sm">Tên *</span><input v-model="f.lead_name" class="inp"/></label>
<label class="block mb-2"><span class="text-sm">Email</span><input v-model="f.email" class="inp"/></label>
<label class="block mb-2"><span class="text-sm">SĐT</span><input v-model="f.mobile" class="inp"/></label>
<label class="block mb-2"><span class="text-sm">Công ty</span><input v-model="f.company_name" class="inp"/></label>
<div class="flex justify-end gap-2 mt-5"><Button variant="subtle" @click="show=false">Hủy</Button><Button variant="solid" :loading="saving" @click="save">Lưu</Button></div></div></div></div></template>
<script setup>
import {ref} from 'vue'; import {Button,FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const rows=ref([]),loading=ref(false),st=ref('')
const statuses=[{value:'',label:'Tất cả'},{value:'Lead',label:'Mới'},{value:'Open',label:'Mở'},{value:'Replied',label:'Đã LH'},{value:'Opportunity',label:'Cơ hội'},{value:'Quotation',label:'Báo giá'},{value:'Converted',label:'Đã chuyển'}]
async function reload(){loading.value=true;try{const r=await callApi('crm_ui.api.get_leads',{status:st.value},'GET');rows.value=(r?.entries||[]).map(l=>({...l,_ns:l.status}))}finally{loading.value=false}};reload()
async function move(l){await callApi('crm_ui.api.move_lead_status',{name:l.name,status:l._ns});reload()}
async function convert(l){try{await callApi('crm_ui.api.convert_lead_to_opportunity',{name:l.name});reload()}catch(e){alert('Lỗi: '+(e?.message||e))}}
const show=ref(false),saving=ref(false);const f=ref({lead_name:'',email:'',mobile:'',company_name:''})
function openCreate(){f.value={lead_name:'',email:'',mobile:'',company_name:''};show.value=true}
async function save(){if(!f.value.lead_name)return;saving.value=true;try{await callApi('crm_ui.api.create_lead',{...f.value});show.value=false;reload()}catch(e){alert('Lỗi: '+(e?.message||e))}finally{saving.value=false}}
function badge(s){return{Lead:'bg-blue-100 text-blue-700',Open:'bg-indigo-100 text-indigo-700',Replied:'bg-amber-100 text-amber-700',Opportunity:'bg-violet-100 text-violet-700',Quotation:'bg-teal-100 text-teal-700',Converted:'bg-emerald-100 text-emerald-700'}[s]||'bg-gray-100'}
</script>
