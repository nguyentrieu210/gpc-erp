<!-- GPC SHARED — LineItemsEditor. Bảng dòng hàng (item + SL + ĐVT + đơn giá + thành tiền) cho SO/PO/Quotation/Invoice.
  v-model = mảng dòng [{item_code,item_name,qty,uom,rate,amount}]. Tự tính amount & tổng. -->
<template>
  <div class="space-y-2">
    <div class="rounded-lg border bg-white overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr>
            <th class="px-2 py-2 text-left">Mặt hàng</th>
            <th class="px-2 py-2 text-right w-24">SL</th>
            <th v-if="showUom" class="px-2 py-2 text-left w-24">ĐVT</th>
            <th class="px-2 py-2 text-right w-32">Đơn giá</th>
            <th class="px-2 py-2 text-right w-36">Thành tiền</th>
            <th v-if="editable" class="w-10"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!lines.length"><td :colspan="editable ? 6 : 5" class="py-6 text-center text-gray-400">Chưa có dòng hàng</td></tr>
          <tr v-for="(ln, i) in lines" :key="i">
            <td class="px-2 py-1.5 min-w-[200px]">
              <EntityPicker v-if="editable" :model-value="ln.item_code" :api="itemApi" :result-key="itemResultKey"
                value-key="item_code" label-key="item_name" sub-key="item_code" placeholder="Chọn hàng…"
                :display-text="ln.item_name" icon="package" @select="(r) => onPickItem(i, r)" />
              <div v-else><div class="font-medium">{{ ln.item_name || ln.item_code }}</div><div class="text-xs text-gray-500">{{ ln.item_code }}</div></div>
            </td>
            <td class="px-2 py-1.5 text-right"><input v-if="editable" v-model.number="ln.qty" type="number" min="0" step="any" class="inp text-right" @input="recalc(i)" /><span v-else>{{ ln.qty }}</span></td>
            <td v-if="showUom" class="px-2 py-1.5"><span class="text-gray-600">{{ ln.uom }}</span></td>
            <td class="px-2 py-1.5 text-right"><input v-if="editable" v-model.number="ln.rate" type="number" min="0" step="any" class="inp text-right" @input="recalc(i)" /><span v-else>{{ money(ln.rate) }}</span></td>
            <td class="px-2 py-1.5 text-right font-medium">{{ money(ln.amount) }}</td>
            <td v-if="editable" class="px-2 py-1.5 text-center"><button class="text-gray-400 hover:text-rose-500" @click="removeLine(i)"><FeatherIcon name="trash-2" class="h-4 w-4" /></button></td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="bg-gray-50 font-semibold">
            <td :colspan="showUom ? 4 : 3" class="px-2 py-2 text-right">Tổng cộng</td>
            <td class="px-2 py-2 text-right">{{ money(total) }}</td>
            <td v-if="editable"></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <button v-if="editable" class="btn-secondary px-3 py-1.5 rounded-lg text-sm inline-flex items-center gap-1" @click="addLine">
      <FeatherIcon name="plus" class="h-4 w-4" /> Thêm dòng
    </button>
  </div>
</template>
<script setup>
import { ref, computed, watch } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import EntityPicker from './EntityPicker.vue'
import { callApi } from '../composables/useFrappeApi'
import { money } from '../utils/format'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  editable: { type: Boolean, default: true },
  showUom: { type: Boolean, default: true },
  itemApi: { type: String, default: 'kho.api.get_items' },
  itemResultKey: { type: String, default: 'items' },
  priceApi: String,          // vd 'kinhdoanh.api.get_selling_price' — GET {item_code} -> {rate} hoặc số
  priceParams: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

const lines = ref(normalize(props.modelValue))
function normalize(arr) { return (arr || []).map((l) => ({ item_code: l.item_code || '', item_name: l.item_name || '', qty: l.qty ?? 1, uom: l.uom || '', rate: l.rate ?? 0, amount: l.amount ?? (Number(l.qty || 0) * Number(l.rate || 0)) })) }
watch(() => props.modelValue, (v) => { if (v !== lines.value) lines.value = normalize(v) })

const total = computed(() => lines.value.reduce((s, l) => s + Number(l.amount || 0), 0))
function sync() { emit('update:modelValue', lines.value) }
function recalc(i) { const l = lines.value[i]; l.amount = Number(l.qty || 0) * Number(l.rate || 0); sync() }
function addLine() { lines.value.push({ item_code: '', item_name: '', qty: 1, uom: '', rate: 0, amount: 0 }); sync() }
function removeLine(i) { lines.value.splice(i, 1); sync() }

async function onPickItem(i, r) {
  const l = lines.value[i]
  if (!r) { l.item_code = ''; l.item_name = ''; sync(); return }
  l.item_code = r.item_code || r.name
  l.item_name = r.item_name || r.item_code
  l.uom = r.stock_uom || r.uom || l.uom
  if (r.rate || r.standard_rate || r.valuation_rate) l.rate = r.rate || r.standard_rate || r.valuation_rate
  if (props.priceApi) {
    try {
      const res = await callApi(props.priceApi, { item_code: l.item_code, ...props.priceParams }, 'GET')
      const rate = typeof res === 'number' ? res : (res?.rate ?? res?.price_list_rate)
      if (rate) l.rate = rate
    } catch (e) {}
  }
  recalc(i)
}
</script>
