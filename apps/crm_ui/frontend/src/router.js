import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/leads', name: 'Leads', component: () => import('./pages/Leads.vue') },
  { path: '/leads/:name', name: 'LeadDetail', component: () => import('./pages/LeadDetail.vue') },
  { path: '/opportunities', name: 'Opportunities', component: () => import('./pages/Opportunities.vue') },
  { path: '/opportunities/:name', name: 'OpportunityDetail', component: () => import('./pages/OpportunityDetail.vue') },
  { path: '/customers', name: 'Customers', component: () => import('./pages/Customers.vue') },
  { path: '/customers/:name', name: 'CustomerDetail', component: () => import('./pages/CustomerDetail.vue') },
  { path: '/contacts', name: 'Contacts', component: () => import('./pages/Contacts.vue') },
  { path: '/activities', name: 'Activities', component: () => import('./pages/Activities.vue') },
  { path: '/campaigns', name: 'Campaigns', component: () => import('./pages/Campaigns.vue') },
  { path: '/setup', name: 'CRMSetup', component: () => import('./pages/CRMSetup.vue') },
]
const router = createRouter({ history: createWebHistory('/crm_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
