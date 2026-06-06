<!-- GPC SHARED — Avatar. Ảnh nếu có src, ngược lại initials + màu hash từ tên. -->
<template>
  <div class="rounded-full overflow-hidden flex items-center justify-center font-semibold text-white shrink-0"
       :style="{ width: size + 'px', height: size + 'px', fontSize: (size * 0.4) + 'px', background: src ? '#e5e7eb' : color }">
    <img v-if="src" :src="imgSrc" class="w-full h-full object-cover" alt="" />
    <span v-else>{{ ini }}</span>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { initials, avatarColor } from '../utils/format'
const props = defineProps({
  name: String,
  src: String, // url hoặc base64 (không có tiền tố data:)
  size: { type: Number, default: 36 },
})
const ini = computed(() => initials(props.name))
const color = computed(() => avatarColor(props.name))
const imgSrc = computed(() => {
  if (!props.src) return ''
  return props.src.startsWith('data:') || props.src.startsWith('http') || props.src.startsWith('/')
    ? props.src : 'data:image/jpeg;base64,' + props.src
})
</script>
