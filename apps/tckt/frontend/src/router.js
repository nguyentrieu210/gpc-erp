import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/journal-entries', name: 'JEs', component: () => import('./pages/JournalEntries.vue') },
  { path: '/general-ledger', name: 'GL', component: () => import('./pages/GeneralLedger.vue') },
  { path: '/trial-balance', name: 'TB', component: () => import('./pages/TrialBalance.vue') },
  { path: '/chart-of-accounts', name: 'COA', component: () => import('./pages/ChartOfAccounts.vue') },
  { path: '/profit-loss', name: 'PL', component: () => import('./pages/ProfitLoss.vue') },
  { path: '/balance-sheet', name: 'BS', component: () => import('./pages/BalanceSheet.vue') },
  { path: '/bank-reconciliation', name: 'BankRecon', component: () => import('./pages/BankReconciliation.vue') },
  { path: '/setup', name: 'TcktSetup', component: () => import('./pages/TcktSetup.vue') },
]
const router = createRouter({ history: createWebHistory('/tckt_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
