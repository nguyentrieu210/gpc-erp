/**
 * GPC SHARED — barrel export.
 * Import gọn: import { DataTable, DetailLayout, useFrappeApi, fmtVnd } from '@shared'
 * (alias @shared trỏ tới apps/<app>/frontend/src/_shared — xem vite.config.js + shared/sync.sh)
 */
export { useFrappeApi, callApi } from './composables/useFrappeApi'
export { useToast } from './composables/useToast'
export { formatDate, formatDateTime, today } from './utils/date'
export { fmtVnd, money, pct, initials, avatarColor } from './utils/format'
export { printHtml } from './utils/printHtml'

export { default as PageHeader } from './components/PageHeader.vue'
export { default as StatusBadge } from './components/StatusBadge.vue'
export { default as Avatar } from './components/Avatar.vue'
export { default as StatCard } from './components/StatCard.vue'
export { default as ActivityTimeline } from './components/ActivityTimeline.vue'
export { default as FormModal } from './components/FormModal.vue'
export { default as EntityPicker } from './components/EntityPicker.vue'
export { default as DataTable } from './components/DataTable.vue'
export { default as DetailLayout } from './components/DetailLayout.vue'
export { default as LineItemsEditor } from './components/LineItemsEditor.vue'
export { default as Kanban } from './components/Kanban.vue'
