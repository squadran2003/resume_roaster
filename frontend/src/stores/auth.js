import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

const isBrowser = typeof window !== 'undefined'

export const useAuthStore = defineStore('auth', () => {
  // Guard localStorage: this store is instantiated during static prerender (Node),
  // where browser globals are unavailable.
  const accessToken = ref(isBrowser ? localStorage.getItem('access_token') : null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const paymentsEnabled = computed(() => user.value?.payments_enabled ?? false)

  async function login(email, password, turnstileToken) {
    const payload = { email, password }
    if (turnstileToken) payload.turnstile_token = turnstileToken
    const { data } = await authApi.login(payload)
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchMe()
  }

  async function fetchMe() {
    const { data } = await authApi.getMe()
    user.value = data
  }

  function logout() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    // Use window.location to ensure router guard re-evaluates cleanly
    window.location.href = '/login'
  }

  // Restore user on page load if token exists
  if (accessToken.value) {
    fetchMe().catch(logout)
  }

  async function googleLogin(credential) {
    const { data } = await authApi.googleLogin(credential)
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchMe()
  }

  return { accessToken, user, isAuthenticated, paymentsEnabled, login, googleLogin, logout, fetchMe }
})
