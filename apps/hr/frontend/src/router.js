import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser } from './data/session'

const routes = [
  { path: '/', name: 'Home', component: () => import('./pages/Home.vue') },
  { path: '/employees', name: 'Employees', component: () => import('./pages/Employees.vue') },
  { path: '/employees/:id', name: 'EmployeeDetail', component: () => import('./pages/EmployeeDetail.vue') },
  { path: '/leaves', name: 'Leaves', component: () => import('./pages/Leaves.vue') },
  { path: '/recruitment', name: 'Recruitment', component: () => import('./pages/Recruitment.vue') },
  { path: '/applicant/:id', name: 'ApplicantDetail', component: () => import('./pages/ApplicantDetail.vue') },
  { path: '/attendance', name: 'Attendance', component: () => import('./pages/Attendance.vue') },
  { path: '/payroll', name: 'Payroll', component: () => import('./pages/Payroll.vue') },
  { path: '/performance', name: 'Performance', component: () => import('./pages/Performance.vue') },
  { path: '/expenses', name: 'Expenses', component: () => import('./pages/Expenses.vue') },
  { path: '/benefits', name: 'Benefits', component: () => import('./pages/Benefits.vue') },
  { path: '/seniority', name: 'Seniority', component: () => import('./pages/Seniority.vue') },
  { path: '/hr-setup', name: 'HRSetup', component: () => import('./pages/HRSetup.vue') },
  { path: '/payroll-config', name: 'PayrollConfig', component: () => import('./pages/PayrollConfig.vue') },
  { path: '/hr-movement', name: 'HRMovement', component: () => import('./pages/HRMovement.vue') },
  // Trang công khai — không cần đăng nhập
  { path: '/onboarding', name: 'Onboarding', component: () => import('./pages/Onboarding.vue'), meta: { public: true } },
]

const router = createRouter({
  history: createWebHistory('/hr_app'),
  routes,
})

router.beforeEach((to) => {
  // Bỏ qua kiểm tra auth cho các trang public
  if (to.meta?.public) return true
  const user = sessionUser()
  if (!user) {
    window.location.href = '/portal_app/login'
    return false
  }
})

export default router

