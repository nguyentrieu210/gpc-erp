<!-- GPC SHARED — DetailLayout. Trang chi tiết: header(back+tiêu đề+status+actions) + banner + 2 cột (main + sidebar). -->
<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <PageHeader :title="title" :subtitle="subtitle" :icon="icon" :icon-class="iconClass" :back="back">
      <slot name="actions" />
    </PageHeader>

    <div v-if="loading" class="flex-1 flex items-center justify-center py-20"><LoadingIndicator class="w-8 h-8" /></div>
    <template v-else>
      <!-- Banner trạng thái -->
      <div class="bg-gradient-to-r text-white px-4 py-4" :class="bannerGradient">
        <div class="max-w-6xl mx-auto flex items-center gap-3 flex-wrap">
          <div class="min-w-0">
            <div class="text-lg font-bold truncate">{{ heading || title }}</div>
            <div v-if="meta" class="text-sm text-white/80 truncate">{{ meta }}</div>
          </div>
          <StatusBadge v-if="status" :status="status" :tone="statusTone" class="!bg-white/20 !text-white" />
          <div v-if="amount !== undefined && amount !== null" class="ml-auto text-right">
            <div class="text-xs text-white/70">{{ amountLabel }}</div>
            <div class="text-xl font-bold">{{ amount }}</div>
          </div>
          <slot name="banner" />
        </div>
      </div>

      <!-- Body -->
      <main class="flex-1 p-4">
        <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-2 space-y-4"><slot /></div>
          <div class="space-y-4"><slot name="sidebar" /></div>
        </div>
      </main>
    </template>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { LoadingIndicator } from 'frappe-ui'
import PageHeader from './PageHeader.vue'
import StatusBadge from './StatusBadge.vue'
const props = defineProps({
  loading: Boolean,
  title: String, subtitle: String, heading: String, meta: String,
  icon: String, iconClass: { type: String, default: 'text-indigo-600' },
  back: { type: [String, Boolean], default: '/' },
  status: String, statusTone: String,
  amount: [String, Number], amountLabel: { type: String, default: 'Tổng tiền' },
  gradient: { type: String, default: 'from-indigo-600 to-violet-600' },
})
const bannerGradient = computed(() => props.gradient)
</script>
