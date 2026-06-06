import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'

const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/suppliers', name: 'Suppliers', component: () => import('./pages/Suppliers.vue') },
  { path: '/suppliers/:id', name: 'SupplierDetail', component: () => import('./pages/SupplierDetail.vue') },
  { path: '/purchase-requests', name: 'PurchaseRequests', component: () => import('./pages/PurchaseRequests.vue') },
  { path: '/purchase-requests/:name', name: 'PRDetail', component: () => import('./pages/PurchaseRequestDetail.vue') },
  { path: '/purchase-orders', name: 'PurchaseOrders', component: () => import('./pages/PurchaseOrders.vue') },
  { path: '/po/:id', name: 'PODetail', component: () => import('./pages/PODetail.vue') },
  { path: '/purchase-receipts', name: 'PurchaseReceipts', component: () => import('./pages/PurchaseReceipts.vue') },
  { path: '/purchase-receipts/:name', name: 'PRRDetail', component: () => import('./pages/PurchaseReceiptDetail.vue') },
  { path: '/purchase-invoices', name: 'PurchaseInvoices', component: () => import('./pages/PurchaseInvoices.vue') },
  { path: '/purchase-invoices/:name', name: 'PIDetail', component: () => import('./pages/PurchaseInvoiceDetail.vue') },
  { path: '/payables', name: 'Payables', component: () => import('./pages/Payables.vue') },
  { path: '/rfq', name: 'RFQ', component: () => import('./pages/RFQ.vue') },
  { path: '/setup', name: 'MuaHangSetup', component: () => import('./pages/MuaHangSetup.vue') },
]

const router = createRouter({ history: createWebHistory('/muahang_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
