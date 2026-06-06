import './index.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { FrappeUI, Button, FormControl, ErrorMessage, Badge, FeatherIcon, LoadingIndicator, setConfig, frappeRequest } from 'frappe-ui'
import { formatDate, formatDateTime } from './utils/date'

// CSRF token — fetch từ API trước khi mount app (sid cookie HttpOnly, ko đọc được từ JS)
async function initCSRF() {
  try {
    const res = await fetch('/api/method/hr.api.get_csrf_token')
    const data = await res.json()
    window.csrf_token = data.message || ''
  } catch { /* fallback: thử các API khác */ }
}

const pinia = createPinia()
const app = createApp(App)

setConfig('resourceFetcher', (options) => frappeRequest({ ...options, method: options.method || 'GET' }))
app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.component('Button', Button)
app.component('Badge', Badge)
app.component('FeatherIcon', FeatherIcon)
app.component('LoadingIndicator', LoadingIndicator)

// Global properties for date/time formatting
app.config.globalProperties.$fmtDate = formatDate
app.config.globalProperties.$fmtDateTime = formatDateTime

// Mount sau khi có CSRF token
initCSRF().then(() => app.mount('#app'))
