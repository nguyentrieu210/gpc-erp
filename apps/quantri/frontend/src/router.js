import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/users', name: 'Users', component: () => import('./pages/Users.vue') },
  { path: '/users/:id', name: 'UserDetail', component: () => import('./pages/UserDetail.vue') },
  { path: '/roles', name: 'Roles', component: () => import('./pages/Roles.vue') },
]
const router = createRouter({ history: createWebHistory('/quantri_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
