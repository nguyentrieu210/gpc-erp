<!-- GPC SHARED — DataTable (workhorse).
  Client-side: search + filter + sort + phân trang + chọn nhiều. Cũng phát @search/@filter cho server-side.
  Slots: toolbar (thêm nút), col-<key> (render ô tùy biến: {row,value}), actions ({row}), bulk ({selected,clear}). -->
<template>
  <div class="space-y-3">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-2">
      <div v-if="searchable" class="relative flex-1 min-w-[180px]">
        <FeatherIcon name="search" class="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input v-model="q" :placeholder="searchPlaceholder" class="inp pl-9" @input="onSearch" />
      </div>
      <select v-for="f in filters" :key="f.key" v-model="activeFilters[f.key]" class="inp w-auto" @change="emit('filter', { key: f.key, value: activeFilters[f.key] })">
        <option value="">{{ f.label }}: Tất cả</option>
        <option v-for="o in f.options" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
      <slot name="toolbar" />
    </div>

    <!-- Bulk bar -->
    <div v-if="selectable && selected.length" class="flex items-center gap-2 px-3 py-2 bg-indigo-50 rounded-lg text-sm">
      <span class="font-medium text-indigo-700">Đã chọn {{ selected.length }}</span>
      <slot name="bulk" :selected="selected" :clear="clearSel" />
      <button class="ml-auto text-gray-500 hover:text-gray-800" @click="clearSel">Bỏ chọn</button>
    </div>

    <!-- Table -->
    <div class="rounded-xl border bg-white overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr>
              <th v-if="selectable" class="w-10 px-3 py-2"><input type="checkbox" :checked="allChecked" @change="toggleAll" /></th>
              <th v-for="c in columns" :key="c.key" class="px-3 py-2 text-left select-none" :class="[c.align === 'right' ? 'text-right' : c.align === 'center' ? 'text-center' : 'text-left', c.sortable !== false ? 'cursor-pointer' : '']" :style="c.width ? { width: c.width } : {}" @click="c.sortable !== false && sortBy(c.key)">
                <span class="inline-flex items-center gap-1">{{ c.label }}
                  <FeatherIcon v-if="sortKey === c.key" :name="sortDir === 'asc' ? 'chevron-up' : 'chevron-down'" class="h-3 w-3" />
                </span>
              </th>
              <th v-if="$slots.actions" class="px-3 py-2 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="colCount" class="py-10 text-center"><LoadingIndicator class="inline w-6 h-6" /></td></tr>
            <tr v-else-if="!paged.length"><td :colspan="colCount" class="py-10 text-center text-gray-400">{{ emptyText }}</td></tr>
            <tr v-for="row in paged" :key="row[rowKey]" :class="clickable ? 'cursor-pointer' : ''" @click="clickable && emit('row-click', row)">
              <td v-if="selectable" class="px-3 py-2" @click.stop><input type="checkbox" :checked="isSel(row)" @change="toggleRow(row)" /></td>
              <td v-for="c in columns" :key="c.key" class="px-3 py-2" :class="c.align === 'right' ? 'text-right' : c.align === 'center' ? 'text-center' : ''">
                <slot :name="'col-' + c.key" :row="row" :value="row[c.key]">{{ c.fmt ? c.fmt(row[c.key], row) : (row[c.key] ?? '') }}</slot>
              </td>
              <td v-if="$slots.actions" class="px-3 py-2 text-right" @click.stop><slot name="actions" :row="row" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-3 py-2 border-t text-sm text-gray-600">
        <span>{{ filtered.length }} dòng · trang {{ page }}/{{ totalPages }}</span>
        <div class="flex gap-1">
          <button class="btn-secondary px-2 py-1 rounded disabled:opacity-40" :disabled="page <= 1" @click="page--"><FeatherIcon name="chevron-left" class="h-4 w-4" /></button>
          <button class="btn-secondary px-2 py-1 rounded disabled:opacity-40" :disabled="page >= totalPages" @click="page++"><FeatherIcon name="chevron-right" class="h-4 w-4" /></button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { FeatherIcon, LoadingIndicator } from 'frappe-ui'

const props = defineProps({
  rows: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  loading: Boolean,
  rowKey: { type: String, default: 'name' },
  searchable: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: 'Tìm kiếm…' },
  searchKeys: { type: Array, default: null }, // null = tìm trên mọi cột chuỗi
  filters: { type: Array, default: () => [] },
  pageSize: { type: Number, default: 20 },
  selectable: Boolean,
  clickable: { type: Boolean, default: true },
  emptyText: { type: String, default: 'Không có dữ liệu' },
  serverSide: Boolean, // true: không lọc client (parent lo qua @search/@filter)
})
const emit = defineEmits(['row-click', 'search', 'filter', 'update:selected'])

const q = ref('')
const activeFilters = reactive({})
const sortKey = ref('')
const sortDir = ref('asc')
const page = ref(1)
const selected = ref([])
let searchTimer = null

function onSearch() {
  page.value = 1
  if (props.serverSide) { if (searchTimer) clearTimeout(searchTimer); searchTimer = setTimeout(() => emit('search', q.value), 300) }
}
function sortBy(k) { if (sortKey.value === k) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'; else { sortKey.value = k; sortDir.value = 'asc' } }

const filtered = computed(() => {
  if (props.serverSide) return props.rows
  let r = props.rows || []
  const text = q.value.trim().toLowerCase()
  if (text) {
    const keys = props.searchKeys || props.columns.map((c) => c.key)
    r = r.filter((row) => keys.some((k) => String(row[k] ?? '').toLowerCase().includes(text)))
  }
  for (const f of props.filters) {
    const v = activeFilters[f.key]
    if (v !== undefined && v !== '') r = r.filter((row) => String(row[f.key] ?? '') === String(v))
  }
  if (sortKey.value) {
    r = [...r].sort((a, b) => {
      const av = a[sortKey.value], bv = b[sortKey.value]
      const na = Number(av), nb = Number(bv)
      let cmp
      if (!isNaN(na) && !isNaN(nb) && av !== '' && bv !== '') cmp = na - nb
      else cmp = String(av ?? '').localeCompare(String(bv ?? ''), 'vi')
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  }
  return r
})
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / props.pageSize)))
const paged = computed(() => props.serverSide ? filtered.value : filtered.value.slice((page.value - 1) * props.pageSize, page.value * props.pageSize))
const colCount = computed(() => props.columns.length + (props.selectable ? 1 : 0) + 1)

watch(filtered, () => { if (page.value > totalPages.value) page.value = 1 })

// selection
function isSel(row) { return selected.value.some((s) => s[props.rowKey] === row[props.rowKey]) }
function toggleRow(row) { isSel(row) ? (selected.value = selected.value.filter((s) => s[props.rowKey] !== row[props.rowKey])) : selected.value.push(row); emit('update:selected', selected.value) }
const allChecked = computed(() => paged.value.length > 0 && paged.value.every(isSel))
function toggleAll() { allChecked.value ? (selected.value = selected.value.filter((s) => !paged.value.some((r) => r[props.rowKey] === s[props.rowKey]))) : paged.value.forEach((r) => { if (!isSel(r)) selected.value.push(r) }); emit('update:selected', selected.value) }
function clearSel() { selected.value = []; emit('update:selected', []) }
</script>
