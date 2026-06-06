import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'

const routes = [
  {
    path: '/',
    name: 'Launcher',
    component: () => import('./pages/Launcher.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./pages/Login.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/portal_app'),
  routes,
})

router.beforeEach((to) => {
  const user = sessionUser()
  if (!user && to.name !== 'Login') return { name: 'Login' }
  if (user && to.name === 'Login') return { name: 'Launcher' }
})

export default router
