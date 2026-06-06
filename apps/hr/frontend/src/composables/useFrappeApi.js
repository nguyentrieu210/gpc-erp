/**
 * GPC Standard — useFrappeApi
 *
 * Gọi Frappe API qua frappeRequest (frappe-ui) với ref reactive.
 * Đây là pattern CHUẨN cho mọi app GPC.
 *
 * Dùng frappeRequest thay vì createResource vì:
 * - createResource có bug với app mới (reactive không cập nhật đúng)
 * - frappeRequest là low-level API của frappe-ui, chạy ổn định
 * - Tự động unwrap message, handle CSRF, auth cookie
 *
 * Usage:
 *   const { data, loading, error, fetch } = useFrappeApi('duan.api.get_dashboard')
 *   // hoặc:
 *   const api = useFrappeApi('duan.api.get_projects', { auto: true, params: { search: '' } })
 */

import { ref, onMounted, shallowRef } from 'vue'
import { frappeRequest } from 'frappe-ui'

export function useFrappeApi(urlOrOptions, opts = {}) {
  const url = typeof urlOrOptions === 'string' ? urlOrOptions : urlOrOptions?.url
  const options = typeof urlOrOptions === 'object' && urlOrOptions !== null ? urlOrOptions : opts
  const params = options.params || {}
  const auto = options.auto !== false
  const initialData = options.initialData !== undefined ? options.initialData : null
  const onError = options.onError || null
  const onSuccess = options.onSuccess || null

  const data = shallowRef(initialData)
  const loading = ref(false)
  const error = ref(null)

  async function fetch(queryParams = {}) {
    const mergedParams = { ...params, ...queryParams }
    loading.value = true
    error.value = null

    try {
      const result = await frappeRequest({
        url,
        method: options.method || 'GET',
        params: mergedParams,
      })
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e
      onError?.(e)
      return null
    } finally {
      loading.value = false
    }
  }

  if (auto) {
    onMounted(() => { fetch().catch(() => {}) })
  }

  return { data, loading, error, fetch }
}
