import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('../views/LandingView.vue'),
    meta: { public: true, guestOnly: true },
  },
  {
    path: '/login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, guestOnly: true },
  },
  {
    path: '/register',
    component: () => import('../views/RegisterView.vue'),
    meta: { public: true, guestOnly: true },
  },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/upload', component: () => import('../views/UploadResumeView.vue') },
  { path: '/analysis/new', component: () => import('../views/NewAnalysisView.vue') },
  { path: '/analysis/:id', component: () => import('../views/AnalysisResultView.vue') },
  { path: '/account', component: () => import('../views/AccountView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return '/dashboard'
  }
})

export default router
