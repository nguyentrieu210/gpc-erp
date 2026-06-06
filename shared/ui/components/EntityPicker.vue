<!-- GPC SHARED — EntityPicker. Ô tìm-chọn 1 bản ghi qua API (item/customer/supplier/account…). -->
<template>
  <div class="relative" ref="root">
    <div class="inp flex items-center gap-2 cursor-text" :class="disabled ? 'opacity-60' : ''" @click="open">
      <FeatherIcon v-if="icon" :name="icon" class="h-4 w-4 text-gray-400 shrink-0" />
      <input v-model="q" :placeholder="selectedLabel || placeholder" :disabled="disabled"
        class="flex-1 bg-transparent outline-none text-sm min-w-0" @focus="open" @input="onType" />
      <button v-if="modelValue && !disabled" class="text-gray-400 hover:text-rose-500" @click.stop="clear"><FeatherIcon name="x" class="h-4 w-4" /></button>
    </div>
    <div v-if="showList" class="absolute z-30 mt-1 w-full bg-white border rounded-lg shadow-lg max-h-64 overflow-auto">
      <div v-if="loading" class="px-3 py-3 text-center text-gray-400 text-sm"><LoadingIndicator class="inline w-4 h-4" /></div>
      <div v-else-if="!results.length" class="px-3 py-3 text-center text-gray-400 text-sm">Không có kết quả</div>
      <button v-for="r in results" :key="r[valueKey]" type="button"
        class="w-full text-left px-3 py-2 hover:bg-indigo-50 border-b last:border-0"
        @click="pick(r)">
        <div class="text-sm font-medium truncate">{{ r[labelKey] || r[valueKey] }}</div>
        <div v-if="subKey && r[subKey]" class="text-xs text-gray-500 truncate">{{ r[subKey] }}</div>
      </button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { callApi } from '../composables/useFrappeApi'

const props = defineProps({
  modelValue: String,
  api: { type: String, required: true },     // endpoint GET trả {entries:[...]} hoặc mảng
  params: { type: Object, default: () => ({}) },
  resultKey: { type: String, default: 'entries' }, // '' nếu API trả mảng trực tiếp
  valueKey: { type: String, default: 'name' },
  labelKey: { type: String, default: 'name' },
  subKey: String,
  placeholder: { type: String, default: 'Tìm…' },
  displayText: String,   // nhãn hiển thị cho giá trị đang chọn (nếu biết sẵn)
  icon: String,
  disabled: Boolean,
  searchParam: { type: String, default: 'search' },
})
const emit = defineEmits(['update:modelValue', 'select'])

const root = ref(null)
const q = ref('')
const results = ref([])
const loading = ref(false)
const showList = ref(false)
const selectedLabel = ref(props.displayText || props.modelValue || '')
let timer = null

watch(() => props.displayText, (v) => { if (v) selectedLabel.value = v })
watch(() => props.modelValue, (v) => { if (!v) selectedLabel.value = ''; else if (!selectedLabel.value) selectedLabel.value = props.displayText || v })

async function load() {
  loading.value = true
  try {
    const res = await callApi(props.api, { ...props.params, [props.searchParam]: q.value, page_length: 20 }, 'GET')
    results.value = props.resultKey ? (res?.[props.resultKey] || []) : (Array.isArray(res) ? res : [])
  } catch (e) { results.value = [] } finally { loading.value = false }
}
function open() { if (props.disabled) return; showList.value = true; if (!results.value.length) load() }
function onType() { if (timer) clearTimeout(timer); timer = setTimeout(load, 300); showList.value = true }
function pick(r) {
  selectedLabel.value = r[props.labelKey] || r[props.valueKey]
  q.value = ''
  showList.value = false
  emit('update:modelValue', r[props.valueKey])
  emit('select', r)
}
function clear() { selectedLabel.value = ''; emit('update:modelValue', ''); emit('select', null) }
function onDoc(e) { if (root.value && !root.value.contains(e.target)) showList.value = false }
onMounted(() => document.addEventListener('click', onDoc))
onUnmounted(() => document.removeEventListener('click', onDoc))
</script>
