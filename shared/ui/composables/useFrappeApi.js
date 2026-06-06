/**
 * GPC SHARED — useFrappeApi (canonical)
 *
 * NGUỒN GỐC DUY NHẤT. Sửa tại shared/ui rồi chạy shared/sync.sh để đồng bộ về các app.
 * KHÔNG sửa bản copy trong apps/<app>/frontend/src/_shared.
 *
 * Gọi Frappe API qua frappeRequest (frappe-ui) — KHÔNG dùng createResource (bug reactive).
 * Export cả 2 pattern để tương thích ngược toàn bộ app:
 *   - useFrappeApi(url|options, opts)  -> { data, loading, error, fetch }
 *   - callApi(url, params, method='POST') -> Promise<result>
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

export async function callApi(url, params = {}, method = 'POST') {
  return await frappeRequest({ url, method, params })
}
