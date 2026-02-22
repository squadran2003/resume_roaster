import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(email, password) {
    const { data } = await authApi.login({ email, password })
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

  return { accessToken, user, isAuthenticated, login, logout, fetchMe }
})
