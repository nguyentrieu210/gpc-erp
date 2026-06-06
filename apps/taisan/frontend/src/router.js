import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/assets', name: 'Assets', component: () => import('./pages/Assets.vue') },
  { path: '/assets/:name', name: 'AssetDetail', component: () => import('./pages/AssetDetail.vue') },
  { path: '/categories', name: 'Categories', component: () => import('./pages/AssetCategories.vue') },
  { path: '/movements', name: 'Movements', component: () => import('./pages/AssetMovements.vue') },
  { path: '/maintenance', name: 'Maintenance', component: () => import('./pages/AssetMaintenance.vue') },
  { path: '/repairs', name: 'Repairs', component: () => import('./pages/AssetRepairs.vue') },
  { path: '/locations', name: 'Locations', component: () => import('./pages/Locations.vue') },
  { path: '/setup', name: 'TaisanSetup', component: () => import('./pages/TaisanSetup.vue') },
]
const router = createRouter({ history: createWebHistory('/taisan_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
