/**
 * GPC SHARED — useToast (canonical). Toast tối giản, không phụ thuộc lib ngoài.
 * Sửa tại shared/ui rồi chạy shared/sync.sh.
 *
 * Usage:
 *   const { toast, ok, err, msg } = useToast()
 *   ok('Đã lưu')          // toast xanh
 *   err('Lỗi: ...')       // toast đỏ
 * Template gắn 1 lần (vd trong App.vue hoặc mỗi trang):
 *   <Toast :toast="toast" />   // hoặc tự render theo toast.value
 */
import { ref } from 'vue'

export function useToast() {
  const toast = ref('')
  let timer = null
  function show(text, ms = 3000) {
    toast.value = text
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => { toast.value = '' }, ms)
  }
  const ok = (t) => show('✅ ' + t)
  const err = (t) => show('❌ ' + t)
  const msg = (t) => show(t)
  return { toast, show, ok, err, msg }
}
