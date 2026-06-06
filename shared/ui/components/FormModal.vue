<!-- GPC SHARED — FormModal. Scaffold modal tạo/sửa: backdrop + header + body(slot) + footer Lưu/Hủy. -->
<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-start justify-center pt-10 px-4 overflow-y-auto bg-black/40" @click.self="$emit('close')">
      <div class="w-full bg-white rounded-2xl shadow-xl mb-10 animate-fadeIn" :class="width">
        <div class="flex items-center gap-2 px-5 py-3 border-b sticky top-0 bg-white rounded-t-2xl z-10">
          <FeatherIcon v-if="icon" :name="icon" class="h-5 w-5 text-indigo-600" />
          <h3 class="text-base font-bold flex-1 truncate">{{ title }}</h3>
          <button class="text-gray-400 hover:text-gray-700" @click="$emit('close')"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>
        <div class="px-5 py-4"><slot /></div>
        <div v-if="!hideFooter" class="flex items-center justify-end gap-2 px-5 py-3 border-t sticky bottom-0 bg-white rounded-b-2xl">
          <slot name="footer">
            <button class="btn-secondary px-4 py-2 rounded-lg text-sm" @click="$emit('close')">Hủy</button>
            <button class="btn-primary px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50" :disabled="saving" @click="$emit('save')">
              {{ saving ? 'Đang lưu…' : saveText }}
            </button>
          </slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>
<script setup>
import { watch, onUnmounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
const props = defineProps({
  show: Boolean, title: String, icon: String,
  width: { type: String, default: 'max-w-2xl' },
  saving: Boolean, saveText: { type: String, default: 'Lưu' },
  hideFooter: Boolean,
})
const emit = defineEmits(['close', 'save'])
function onKey(e) { if (e.key === 'Escape' && props.show) emit('close') }
watch(() => props.show, (v) => {
  if (typeof document === 'undefined') return
  document.body.style.overflow = v ? 'hidden' : ''
  if (v) window.addEventListener('keydown', onKey)
  else window.removeEventListener('keydown', onKey)
})
onUnmounted(() => { if (typeof document !== 'undefined') { document.body.style.overflow = ''; window.removeEventListener('keydown', onKey) } })
</script>
