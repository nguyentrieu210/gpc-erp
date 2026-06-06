import './index.css'
import { formatDate, formatDateTime } from './utils/date'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { FrappeUI, Button, FormControl, ErrorMessage, Badge, FeatherIcon, LoadingIndicator, setConfig, frappeRequest } from 'frappe-ui'

// CSRF token — fetch từ API trước khi mount (sid cookie HttpOnly, JS không đọc được).
// Pattern chuẩn HR — ổn định cho mọi POST (tạo/sửa/chốt phiếu).
async function initCSRF() {
  try {
    const res = await fetch('/api/method/kho.api.get_csrf_token')
    const data = await res.json()
    window.csrf_token = data.message || ''
  } catch { /* fallback: nếu lỗi, POST sẽ tự xin CSRF qua frappe-ui */ }
}

const pinia = createPinia()
const app = createApp(App)
setConfig('resourceFetcher', (o) => frappeRequest({ ...o, method: o.method || 'GET' }))
app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.component('Button', Button)
app.component('FormControl', FormControl)
app.component('ErrorMessage', ErrorMessage)
app.component('Badge', Badge)
app.component('FeatherIcon', FeatherIcon)
app.component('LoadingIndicator', LoadingIndicator)

app.config.globalProperties.$fmtDate = formatDate
app.config.globalProperties.$fmtDateTime = formatDateTime

initCSRF().then(() => app.mount('#app'))
