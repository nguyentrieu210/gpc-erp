<template>
  <div class="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-sans">
    <header class="flex items-center gap-2 border-b bg-white px-4 py-3 sticky top-0 z-10 shadow-sm">
      <button class="text-gray-500 hover:text-gray-800 transition-colors" @click="$router.push('/')">
        <FeatherIcon name="arrow-left" class="h-5 w-5" />
      </button>
      <FeatherIcon name="home" class="h-5 w-5 text-blue-600" />
      <h1 class="text-lg font-bold text-gray-950 flex-1">Sơ đồ Kho & Vị trí</h1>
      <div class="flex gap-2">
        <Button variant="outline" @click="toggleAll(true)" class="text-xs">Mở rộng tất cả</Button>
        <Button variant="outline" @click="toggleAll(false)" class="text-xs">Thu gọn tất cả</Button>
        <Button variant="solid" theme="orange" @click="openCreate" class="flex items-center gap-1 shadow-sm">
          <FeatherIcon name="plus" class="h-4 w-4" />
          <span>Thêm kho gốc</span>
        </Button>
      </div>
    </header>

    <main class="flex-1 p-4 max-w-4xl mx-auto w-full space-y-4">
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden p-4">
        <!-- Loading -->
        <div v-if="loading" class="py-12 text-center"><LoadingIndicator /></div>
        
        <!-- Empty -->
        <div v-else-if="!list?.length" class="py-12 text-center text-gray-400">
          <div class="flex flex-col items-center justify-center gap-2">
            <FeatherIcon name="home" class="h-10 w-10 text-gray-300" />
            <span>Chưa cấu hình kho nào trong hệ thống</span>
          </div>
        </div>

        <!-- Tree View -->
        <div v-else class="divide-y divide-gray-100">
          <div v-for="w in visibleNodes" :key="w.name" 
               class="flex items-center gap-2 py-3 px-2 hover:bg-gray-50 transition-colors group rounded-lg relative cursor-pointer" @click="openEditWarehouse(w)">
            
            <!-- Indentation spacers with guide lines -->
            <div v-for="l in w.level" :key="l" class="w-5 h-6 border-r border-gray-200/80 shrink-0"></div>

            <!-- Expand / Collapse chevron for groups -->
            <button v-if="w.is_group" @click.stop="toggleNode(w.name)"
                    class="w-5 h-5 rounded hover:bg-gray-200 flex items-center justify-center text-gray-500 shrink-0 transition-colors">
              <FeatherIcon :name="expanded[w.name] ? 'chevron-down' : 'chevron-right'" class="h-3 w-3" />
            </button>
            <div v-else class="w-5 shrink-0"></div>

            <!-- Folder / Warehouse Icon -->
            <div class="shrink-0">
              <FeatherIcon :name="w.is_group ? (expanded[w.name] ? 'folder-open' : 'folder') : 'home'" 
                           class="h-5 w-5" 
                           :class="w.is_group ? 'text-amber-500' : 'text-blue-500'" />
            </div>

            <!-- Name and Account Info -->
            <div class="flex-1 min-w-0 pr-2">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-900" :class="w.is_group ? 'text-gray-900' : 'text-gray-800'">
                  {{ w.warehouse_name }}
                </span>
                <span v-if="w.is_group" class="px-1.5 py-0.2 bg-amber-50 border border-amber-200 text-amber-700 text-[10px] font-bold rounded-sm uppercase tracking-wider scale-95 shrink-0">
                  Nhóm
                </span>
                <span v-if="w.disabled" class="px-1.5 py-0.2 bg-red-50 border border-red-200 text-red-600 text-[10px] font-bold rounded-sm uppercase tracking-wider scale-95 shrink-0">
                  Ngừng hoạt động
                </span>
              </div>
              <div class="text-xs text-gray-400 truncate mt-0.5" :title="w.account">
                {{ w.account || 'Chưa liên kết tài khoản kế toán' }}
              </div>
            </div>

            <!-- Action buttons inside node (show on hover) -->
            <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 bg-white pl-2 absolute right-4 top-1/2 -translate-y-1/2 shadow-xs border border-gray-100 rounded p-1" @click.stop>
              <Button v-if="w.is_group" variant="subtle" size="sm" @click="addChild(w)" class="flex items-center gap-0.5 text-xs text-amber-700 hover:text-amber-900">
                <FeatherIcon name="plus" class="h-3 w-3" />
                Thêm kho con
              </Button>
              <Button variant="subtle" size="sm" @click="openEditWarehouse(w)" class="flex items-center gap-0.5 text-xs text-blue-700 hover:text-blue-900">
                <FeatherIcon name="edit-2" class="h-3 w-3" />
                Cấu hình
              </Button>
              <Button variant="subtle" size="sm" @click="toggleWarehouseState(w)" class="text-xs" :class="w.disabled ? 'text-emerald-600' : 'text-red-500'">
                {{ w.disabled ? 'Kích hoạt' : 'Ngừng' }}
              </Button>
            </div>

            <!-- Stock and Value details (Show recursive totals) -->
            <div class="text-right shrink-0 group-hover:opacity-20 transition-opacity">
              <div class="text-sm font-bold" :class="w.is_group ? 'text-gray-400 font-normal font-sans' : 'text-emerald-600 font-mono'">
                {{ fmtVnd(w.recursive_stock_value) }}
              </div>
              <div class="text-xs font-medium font-mono" :class="w.is_group ? 'text-gray-300' : 'text-gray-500'">
                {{ fmtQty(w.recursive_total_qty) }} đơn vị
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Warehouse Modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 animate-fade-in" @click.self="showCreate=false">
      <div class="bg-white rounded-xl w-full max-w-md p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-950">
            {{ form.parent_warehouse ? 'Thêm kho con' : 'Thêm kho gốc' }}
          </h3>
          <button @click="showCreate=false" class="text-gray-400 hover:text-gray-600"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-4">
          <!-- Parent warehouse display -->
          <div v-if="form.parent_warehouse" class="bg-gray-50 p-2.5 rounded-lg border border-gray-200 text-sm">
            <span class="text-xs text-gray-400 block font-medium">Kho cha chỉ định</span>
            <span class="font-bold text-gray-800">{{ getWarehouseLabel(form.parent_warehouse) }}</span>
          </div>

          <Field label="Tên kho / Vị trí *">
            <input v-model="form.warehouse_name" class="inp" placeholder="Ví dụ: Kho tầng 2, Kệ A1..." />
          </Field>

          <Field v-if="!form.parent_warehouse" label="Chọn kho cha (để trống nếu là kho gốc)">
            <select v-model="form.parent_warehouse" class="inp bg-white">
              <option value="">(Không - là kho gốc)</option>
              <option v-for="g in groupWh" :key="g.name" :value="g.name">{{ g.warehouse_name }}</option>
            </select>
          </Field>

          <Field label="Loại kho (Warehouse Type)">
            <select v-model="form.warehouse_type" class="inp bg-white">
              <option value="">(Không phân loại)</option>
              <option value="Store">Kho cửa hàng (Store)</option>
              <option value="Raw Material">Kho nguyên vật liệu (Raw Material)</option>
              <option value="Finished Goods">Kho thành phẩm (Finished Goods)</option>
              <option value="Work in Progress">Hàng đang sản xuất (Work in Progress)</option>
              <option value="Transit">Hàng đi đường (Transit)</option>
              <option value="Scrap">Kho phế liệu (Scrap)</option>
              <option value="Bonded">Kho ngoại quan (Bonded)</option>
            </select>
          </Field>

          <Field label="Tài khoản kế toán (Thừa hưởng từ kho cha/công ty nếu để trống)">
            <select v-model="form.account" class="inp bg-white">
              <option value="">(Tự động kế thừa)</option>
              <option v-for="ac in accounts" :key="ac.name" :value="ac.name">
                {{ ac.account_number }} - {{ ac.account_name }}
              </option>
            </select>
          </Field>

          <div class="bg-gray-50 p-3 rounded-lg border">
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" v-model="form.is_group" class="rounded text-orange-600 focus:ring-orange-500" />
              <div>
                <span class="font-semibold text-sm text-gray-900 block">Là kho nhóm (Chứa kho con)</span>
                <span class="text-xs text-gray-400">Tích chọn nếu muốn tạo nhóm/kệ để chứa các kho hoặc kệ nhỏ hơn bên trong.</span>
              </div>
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <Button variant="subtle" @click="showCreate=false">Hủy</Button>
          <Button variant="solid" theme="orange" :loading="saving" @click="save">Lưu kho</Button>
        </div>
      </div>
    </div>

    <!-- Edit Warehouse Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 animate-fade-in" @click.self="showEditModal=false">
      <div class="bg-white rounded-xl w-full max-w-md p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-950">Cấu hình Kho / Vị trí</h3>
          <button @click="showEditModal=false" class="text-gray-400 hover:text-gray-600"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>

        <div class="space-y-4">
          <Field label="Tên kho / Vị trí *">
            <input v-model="editForm.warehouse_name" class="inp" placeholder="Ví dụ: Kho tầng 2, Kệ A1..." />
          </Field>

          <Field label="Chọn kho cha (để trống nếu là kho gốc)">
            <select v-model="editForm.parent_warehouse" class="inp bg-white">
              <option value="">(Không - là kho gốc)</option>
              <option v-for="g in groupWh.filter(x => x.name !== editForm.name)" :key="g.name" :value="g.name">{{ g.warehouse_name }}</option>
            </select>
          </Field>

          <Field label="Loại kho (Warehouse Type)">
            <select v-model="editForm.warehouse_type" class="inp bg-white">
              <option value="">(Không phân loại)</option>
              <option value="Store">Kho cửa hàng (Store)</option>
              <option value="Raw Material">Kho nguyên vật liệu (Raw Material)</option>
              <option value="Finished Goods">Kho thành phẩm (Finished Goods)</option>
              <option value="Work in Progress">Hàng đang sản xuất (Work in Progress)</option>
              <option value="Transit">Hàng đi đường (Transit)</option>
              <option value="Scrap">Kho phế liệu (Scrap)</option>
              <option value="Bonded">Kho ngoại quan (Bonded)</option>
            </select>
          </Field>

          <Field label="Tài khoản kế toán (Thừa hưởng từ kho cha/công ty nếu để trống)">
            <select v-model="editForm.account" class="inp bg-white">
              <option value="">(Tự động kế thừa)</option>
              <option v-for="ac in accounts" :key="ac.name" :value="ac.name">
                {{ ac.account_number }} - {{ ac.account_name }}
              </option>
            </select>
          </Field>

          <div class="bg-gray-50 p-3 rounded-lg border">
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" v-model="editForm.is_group" class="rounded text-orange-600 focus:ring-orange-500" />
              <div>
                <span class="font-semibold text-sm text-gray-900 block">Là kho nhóm (Chứa kho con)</span>
                <span class="text-xs text-gray-400">Tích chọn nếu muốn biến kho này thành nhóm/kệ để có thể thêm các kho con bên trong.</span>
              </div>
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <Button variant="subtle" @click="showEditModal=false">Hủy</Button>
          <Button variant="solid" theme="orange" :loading="saving" @click="saveEdit">Lưu thay đổi</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, h } from 'vue'
import { Button, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { useFrappeApi, callApi } from '../composables/useFrappeApi'

const { data: list, loading, fetch } = useFrappeApi('kho.api.get_warehouses', {
  initialData: [],
  params: { include_disabled: 1 }
})
const { data: accounts } = useFrappeApi('kho.api.get_stock_accounts', { initialData: [] })
const groupWh = computed(() => (list.value || []).filter(w => w.is_group))

// Map warehouse codes to readable labels
function getWarehouseLabel(name) {
  const w = (list.value || []).find(x => x.name === name)
  return w ? w.warehouse_name : name
}

// Collapsible expanded nodes tracker
const expanded = ref({})

watch(() => list.value, (newVal) => {
  if (newVal) {
    newVal.forEach(w => {
      if (w.is_group && expanded.value[w.name] === undefined) {
        expanded.value[w.name] = true // auto expand group nodes by default
      }
    })
  }
}, { immediate: true })

function toggleNode(name) {
  expanded.value[name] = !expanded.value[name]
}

function toggleAll(expandState) {
  (list.value || []).forEach(w => {
    if (w.is_group) {
      expanded.value[w.name] = expandState
    }
  })
}

// Hierarchical Tree Computed Properties
const tree = computed(() => {
  const items = list.value || []
  const map = {}
  const roots = []
  
  items.forEach(it => {
    map[it.name] = { ...it, children: [], recursive_stock_value: 0, recursive_total_qty: 0 }
  })
  
  items.forEach(it => {
    const mapped = map[it.name]
    if (it.parent_warehouse && map[it.parent_warehouse]) {
      map[it.parent_warehouse].children.push(mapped)
    } else {
      roots.push(mapped)
    }
  })
  
  const computeTotals = (node) => {
    if (!node.is_group) {
      node.recursive_stock_value = node.stock_value || 0
      node.recursive_total_qty = node.total_qty || 0
    } else {
      let valSum = 0
      let qtySum = 0
      node.children.forEach(child => {
        computeTotals(child)
        valSum += child.recursive_stock_value || 0
        qtySum += child.recursive_total_qty || 0
      })
      node.recursive_stock_value = valSum
      node.recursive_total_qty = qtySum
    }
  }
  roots.forEach(r => computeTotals(r))
  
  const sortTree = (nodes) => {
    nodes.sort((a, b) => {
      if (a.is_group && !b.is_group) return -1
      if (!a.is_group && b.is_group) return 1
      return a.warehouse_name.localeCompare(b.warehouse_name)
    })
    nodes.forEach(n => {
      if (n.children.length) sortTree(n.children)
    })
  }
  sortTree(roots)
  
  return roots
})

// Flatten Tree for sequential rendering with Level indentation
const visibleNodes = computed(() => {
  const nodes = []
  
  const traverse = (node, level = 0) => {
    nodes.push({ ...node, level })
    if (node.is_group && expanded.value[node.name]) {
      node.children.forEach(child => traverse(child, level + 1))
    }
  }
  
  tree.value.forEach(root => traverse(root, 0))
  return nodes
})

// Create and Manage Warehouse Functions
const showCreate = ref(false), saving = ref(false)
const form = reactive({ warehouse_name: '', parent_warehouse: '', is_group: false, warehouse_type: '', account: '' })

function openCreate() { 
  Object.assign(form, { warehouse_name: '', parent_warehouse: '', is_group: false, warehouse_type: '', account: '' })
  showCreate.value = true 
}

function addChild(parentWh) {
  Object.assign(form, { warehouse_name: '', parent_warehouse: parentWh.name, is_group: false, warehouse_type: '', account: '' })
  showCreate.value = true
}

async function save() {
  if (!form.warehouse_name) { alert('Nhập tên kho'); return }
  saving.value = true
  try {
    await callApi('kho.api.create_warehouse', { ...form, is_group: form.is_group ? 1 : 0 })
    showCreate.value = false
    await fetch()
  } catch (e) { alert('Lỗi: ' + (e?.message || e)) } finally { saving.value = false }
}

async function toggleWarehouseState(w) {
  try {
    await callApi('kho.api.toggle_warehouse', { name: w.name, disabled: w.disabled ? 0 : 1 })
    await fetch()
  } catch (e) {
    alert('Lỗi: ' + (e?.message || e))
  }
}

// Edit Warehouse Modal state and functions
const showEditModal = ref(false)
const editForm = reactive({
  name: '',
  warehouse_name: '',
  parent_warehouse: '',
  warehouse_type: '',
  account: '',
  is_group: false
})

function openEditWarehouse(w) {
  Object.assign(editForm, {
    name: w.name,
    warehouse_name: w.warehouse_name,
    parent_warehouse: w.parent_warehouse || '',
    warehouse_type: w.warehouse_type || '',
    account: w.account || '',
    is_group: !!w.is_group
  })
  showEditModal.value = true
}

async function saveEdit() {
  if (!editForm.warehouse_name) { alert('Nhập tên kho'); return }
  saving.value = true
  try {
    await callApi('kho.api.update_warehouse', {
      name: editForm.name,
      warehouse_name: editForm.warehouse_name,
      parent_warehouse: editForm.parent_warehouse,
      warehouse_type: editForm.warehouse_type,
      account: editForm.account,
      is_group: editForm.is_group ? 1 : 0
    })
    showEditModal.value = false
    await fetch()
  } catch (e) {
    alert('Lỗi: ' + (e?.message || e))
  } finally {
    saving.value = false
  }
}

function fmtQty(v) { return Number(v || 0).toLocaleString('vi-VN') }
function fmtVnd(v) { return Number(v || 0).toLocaleString('vi-VN') + ' ₫' }

const Field = {
  props: ['label'],
  setup(props, { slots }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'text-sm font-semibold text-gray-600 block mb-1' }, props.label),
      slots.default?.(),
    ])
  },
}
</script>

<style>
.inp {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  padding: 8px 12px;
  font-size: 14px;
  background-color: #fff;
  transition: all 0.2s;
}
.inp:focus {
  outline: none;
  border-color: #ea580c;
  box-shadow: 0 0 0 1px #ea580c;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fadeIn 0.2s ease-out;
}
</style>
