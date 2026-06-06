import './index.css'
import { formatDate, formatDateTime } from './utils/date'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { FrappeUI, Button, FormControl, ErrorMessage, Badge, FeatherIcon, LoadingIndicator, setConfig, frappeRequest } from 'frappe-ui'

// CSRF token — đọc từ cookie để POST API không bị CSRFTokenError
function getCookie(n) { const m = document.cookie.match(new RegExp('(^| )' + n + '=([^;]+)')); return m ? m[2] : '' }
window.csrf_token = getCookie('csrf_token') || getCookie('sid')

const pinia = createPinia()
const app = createApp(App)
setConfig('resourceFetcher', (o) => frappeRequest({ ...o, method: o.method || 'GET' }))
app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.component('Button', Button)
app.component('Badge', Badge)
app.component('FeatherIcon', FeatherIcon)
app.component('LoadingIndicator', LoadingIndicator)

app.config.globalProperties.$fmtDate = formatDate
app.config.globalProperties.$fmtDateTime = formatDateTime
app.mount('#app')
