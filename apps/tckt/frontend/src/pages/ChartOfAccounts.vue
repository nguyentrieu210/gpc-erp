<template>
<div class="flex flex-col min-h-screen bg-gray-50"><header class="flex items-center gap-2 border-b bg-white px-4 py-3"><button @click="$router.push('/')" class="text-gray-500"><FeatherIcon name="arrow-left" class="h-5 w-5"/></button><FeatherIcon name="list" class="h-5 w-5 text-violet-600"/><h1 class="text-lg font-bold flex-1">Hệ thống TK</h1></header>
<main class="flex-1 p-4 max-w-5xl mx-auto"><div class="flex gap-2 mb-3"><select v-model="rt" @change="filter" class="inp w-auto"><option value="">Tất cả</option><option v-for="t in rts" :key="t" :value="t">{{ t }}</option></select></div>
<div class="rounded-xl border bg-white divide-y"><div v-if="loading" class="py-10 text-center"><LoadingIndicator/></div>
<div v-for="a in filtered" :key="a.name" class="flex items-center px-4 py-2.5"><div class="flex-1"><div class="font-medium text-sm">{{ a.account_number }} {{ a.account_name }}</div><div class="text-xs text-gray-400">{{ a.account_type }} · {{ a.root_type }}</div></div></div></div>
</main></div></template>
<script setup>
import {ref,computed} from 'vue'; import {FeatherIcon,LoadingIndicator} from 'frappe-ui'; import {callApi} from '../composables/useFrappeApi'
const all=ref([]),loading=ref(false),rt=ref(''),rts=['Asset','Liability','Equity','Income','Expense']
async function reload(){loading.value=true;try{all.value=(await callApi('tckt.api.get_chart_of_accounts',{},'GET'))?.accounts||[]}finally{loading.value=false}};reload()
const filtered=computed(()=>rt.value?all.value.filter(a=>a.root_type===rt.value):all.value)
async function filter(){}
</script>
