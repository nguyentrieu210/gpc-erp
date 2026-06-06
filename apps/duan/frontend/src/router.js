import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'
const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/projects', name: 'Projects', component: () => import('./pages/Projects.vue') },
  { path: '/projects/:id', name: 'ProjectDetail', component: () => import('./pages/ProjectDetail.vue') },
  { path: '/tasks/:id', name: 'TaskDetail', component: () => import('./pages/TaskDetail.vue') },
]
const router = createRouter({ history: createWebHistory('/duan_app'), routes })
router.beforeEach(() => { if (!sessionUser()) { window.location.href = '/portal_app/login'; return false } })
export default router
