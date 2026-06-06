import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/customers', name: 'Customers', component: () => import('./pages/Customers.vue') },
  { path: '/customers/:name', name: 'CustomerDetail', component: () => import('./pages/CustomerDetail.vue') },
  { path: '/quotations', name: 'Quotations', component: () => import('./pages/Quotations.vue') },
  { path: '/quotations/:name', name: 'QuotationDetail', component: () => import('./pages/QuotationDetail.vue') },
  { path: '/sales-orders', name: 'SOs', component: () => import('./pages/SalesOrders.vue') },
  { path: '/sales-orders/:name', name: 'SODetail', component: () => import('./pages/SalesOrderDetail.vue') },
  { path: '/delivery-notes', name: 'DNs', component: () => import('./pages/DeliveryNotes.vue') },
  { path: '/delivery-notes/:name', name: 'DNDetail', component: () => import('./pages/DeliveryNoteDetail.vue') },
  { path: '/sales-invoices', name: 'SIs', component: () => import('./pages/SalesInvoices.vue') },
  { path: '/sales-invoices/:name', name: 'SIDetail', component: () => import('./pages/SalesInvoiceDetail.vue') },
  { path: '/receivables', name: 'Receivables', component: () => import('./pages/Receivables.vue') },
  { path: '/setup', name: 'SalesSetup', component: () => import('./pages/SalesSetup.vue') },
]
const router = createRouter({ history: createWebHistory('/kinhdoanh_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
