import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'

const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/items', name: 'Items', component: () => import('./pages/Items.vue') },
  { path: '/items/:id', name: 'ItemDetail', component: () => import('./pages/ItemDetail.vue') },
  { path: '/warehouses', name: 'Warehouses', component: () => import('./pages/Warehouses.vue') },
  { path: '/stock-entries', name: 'StockEntries', component: () => import('./pages/StockEntries.vue') },
  { path: '/reconciliation', name: 'StockReconciliation', component: () => import('./pages/StockReconciliation.vue') },
  { path: '/material-requests', name: 'MaterialRequests', component: () => import('./pages/MaterialRequests.vue') },
  { path: '/balance', name: 'StockBalance', component: () => import('./pages/StockBalance.vue') },
  { path: '/ledger', name: 'StockLedger', component: () => import('./pages/StockLedger.vue') },
  { path: '/reorder', name: 'Reorder', component: () => import('./pages/Reorder.vue') },
  { path: '/setup', name: 'KhoSetup', component: () => import('./pages/KhoSetup.vue') },
]

const router = createRouter({
  history: createWebHistory('/kho_app'),
  routes,
})

router.beforeEach(() => {
  if (!sessionUser()) { window.location.href = '/portal_app/login'; return false }
})
export default router
