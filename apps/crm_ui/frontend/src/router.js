import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/leads', name: 'Leads', component: () => import('./pages/Leads.vue') },
  { path: '/opportunities', name: 'Opportunities', component: () => import('./pages/Opportunities.vue') },
  { path: '/customers', name: 'Customers', component: () => import('./pages/Customers.vue') },
  { path: '/setup', name: 'CRMSetup', component: () => import('./pages/CRMSetup.vue') },
]
const router = createRouter({ history: createWebHistory('/crm_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
