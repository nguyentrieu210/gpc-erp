/**
 * GPC Standard — useFrappeApi
 *
 * Gọi Frappe API qua frappeRequest (frappe-ui) với ref reactive.
 * Pattern CHUẨN cho mọi app GPC.
 * Dùng frappeRequest thay vì createResource vì createResource có bug reactive với app mới.
 *
 * Usage:
 *   const { data, loading, error, fetch } = useFrappeApi('muahang.api.get_suppliers')
 *   // POST/write 1 lần:
 *   await callApi('muahang.api.create_supplier', { supplier_name: 'X' })
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
        url, method: options.method || 'GET', params: mergedParams,
      })
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e
      onError?.(e)
      return null
    } finally { loading.value = false }
  }

  if (auto) onMounted(() => { fetch().catch(() => {}) })
  return { data, loading, error, fetch }
}

export async function callApi(url, params = {}, method = 'POST') {
  return await frappeRequest({ url, method, params })
}
