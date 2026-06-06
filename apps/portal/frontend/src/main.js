import './index.css'
import { formatDate, formatDateTime } from './utils/date'


import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  FormControl,
  ErrorMessage,
  FeatherIcon,
  setConfig,
  frappeRequest,
} from 'frappe-ui'

// CSRF token — đọc từ cookie để POST API không bị CSRFTokenError
function getCookie(n) { const m = document.cookie.match(new RegExp('(^| )' + n + '=([^;]+)')); return m ? m[2] : '' }
window.csrf_token = getCookie('csrf_token') || getCookie('sid')

const pinia = createPinia()
const app = createApp(App)

// Use custom request wrapper that defaults to GET (website SPA has no desk CSRF)
function websiteRequest(options = {}) {
  return frappeRequest({
    ...options,
    method: options.method || 'GET',
  })
}
setConfig('resourceFetcher', websiteRequest)

app.use(FrappeUI)
app.use(pinia)
app.use(router)

app.component('Button', Button)
app.component('FormControl', FormControl)
app.component('ErrorMessage', ErrorMessage)
app.component('FeatherIcon', FeatherIcon)


app.config.globalProperties.$fmtDate = formatDate
app.config.globalProperties.$fmtDateTime = formatDateTime
app.mount('#app')
