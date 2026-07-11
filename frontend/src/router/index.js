import { useAuthStore } from '../stores/auth'

// Route table. The router instance itself is created by ViteSSG (see main.js),
// which selects memory history during static prerender and web history in the
// browser. We only export the routes + guard setup here.
export const routes = [
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
  {
    path: '/share/:token',
    component: () => import('../views/ShareView.vue'),
    meta: { public: true },
  },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/upload', component: () => import('../views/UploadResumeView.vue') },
  { path: '/analysis/new', component: () => import('../views/NewAnalysisView.vue') },
  { path: '/analysis/compare', component: () => import('../views/CompareView.vue') },
  { path: '/analysis/:id', component: () => import('../views/AnalysisResultView.vue') },
  { path: '/linkedin', component: () => import('../views/LinkedInView.vue') },
  { path: '/account', component: () => import('../views/AccountView.vue') },
]

export function setupRouterGuards(router) {
  router.beforeEach((to) => {
    const auth = useAuthStore()
    if (!to.meta.public && !auth.isAuthenticated) {
      return '/login'
    }
    if (to.meta.guestOnly && auth.isAuthenticated) {
      return '/dashboard'
    }
  })
}
