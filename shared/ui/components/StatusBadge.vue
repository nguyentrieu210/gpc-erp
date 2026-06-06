<!-- GPC SHARED — StatusBadge. Pill trạng thái, tự đoán màu từ chữ (VI/EN) hoặc nhận tone. -->
<template>
  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap" :class="cls">
    <span v-if="dot" class="w-1.5 h-1.5 rounded-full" :class="dotCls" />
    {{ text || status }}
  </span>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({
  status: String,
  text: String,
  tone: String, // green|amber|red|blue|gray|purple|indigo — ưu tiên nếu truyền
  dot: { type: Boolean, default: true },
})
const TONES = {
  green: 'bg-emerald-100 text-emerald-700', amber: 'bg-amber-100 text-amber-700',
  red: 'bg-rose-100 text-rose-700', blue: 'bg-blue-100 text-blue-700',
  gray: 'bg-gray-100 text-gray-600', purple: 'bg-violet-100 text-violet-700',
  indigo: 'bg-indigo-100 text-indigo-700',
}
const DOTS = {
  green: 'bg-emerald-500', amber: 'bg-amber-500', red: 'bg-rose-500', blue: 'bg-blue-500',
  gray: 'bg-gray-400', purple: 'bg-violet-500', indigo: 'bg-indigo-500',
}
function guess(s) {
  const t = (s || '').toLowerCase()
  if (/(hủy|huỷ|cancel|reject|từ chối|quá hạn|overdue|return|trả|fail|lỗi|do not)/.test(t)) return 'red'
  if (/(đã thanh toán|đã nhận|hoàn thành|completed|paid|approved|active|đã duyệt|đã gửi|chốt|converted|closed won|success)/.test(t)) return 'green'
  if (/(nháp|draft|chờ|pending|một phần|partly|to deliver|to bill|to receive|unpaid|open|mở|awaiting)/.test(t)) return 'amber'
  if (/(submitted|đã ghi sổ|ordered|đã đặt|to order|processing|đang)/.test(t)) return 'blue'
  if (/(opportunity|cơ hội|quotation|báo giá|interested|quan tâm|replied)/.test(t)) return 'purple'
  return 'gray'
}
const tone = computed(() => props.tone || guess(props.status))
const cls = computed(() => TONES[tone.value] || TONES.gray)
const dotCls = computed(() => DOTS[tone.value] || DOTS.gray)
</script>
