import { ref, onMounted } from 'vue'

export function useApi(urlOrOptions, initialParamsOrOptions = {}) {
  let url = ''
  let options = {}
  let params = {}

  if (typeof urlOrOptions === 'object' && urlOrOptions !== null) {
    options = urlOrOptions
    url = options.url
    params = options.params || {}
  } else {
    url = urlOrOptions
    if (initialParamsOrOptions && (initialParamsOrOptions.params || initialParamsOrOptions.method || initialParamsOrOptions.auto)) {
      options = initialParamsOrOptions
      params = options.params || {}
    } else {
      params = initialParamsOrOptions || {}
    }
  }

  const method = options.method || 'GET'
  const auto = options.auto !== undefined ? options.auto : true
  const initialData = options.initialData !== undefined ? options.initialData : null
  const onError = options.onError || (() => {})

  const data = ref(initialData)
  const loading = ref(auto)
  const error = ref(null)

  async function submit(queryParams = {}) {
    const mergedParams = { ...params, ...queryParams }
    loading.value = true
    error.value = null
    try {
      let fetchUrl = `/api/method/${url}`
      let fetchOptions = {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        }
      }

      if (method.toUpperCase() === 'GET') {
        const q = new URLSearchParams()
        for (const [key, val] of Object.entries(mergedParams)) {
          if (val !== undefined && val !== null) {
            q.append(key, val)
          }
        }
        const queryString = q.toString()
        if (queryString) {
          fetchUrl += `?${queryString}`
        }
      } else {
        fetchOptions.body = JSON.stringify(mergedParams)
      }

      const res = await fetch(fetchUrl, fetchOptions)
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      const json = await res.json()
      data.value = json.message !== undefined ? json.message : json
      return data.value
    } catch (e) {
      error.value = e.message || String(e)
      onError(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  if (auto && method.toUpperCase() === 'GET') {
    onMounted(() => {
      submit().catch(() => {})
    })
  }

  return {
    data,
    loading,
    error,
    submit,
    fetch: submit
  }
}
