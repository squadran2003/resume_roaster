<template>
  <div class="auth-layout">
    <!-- Brand panel (desktop) -->
    <div class="auth-brand d-none d-md-flex">
      <div class="d-flex flex-column justify-center pa-12">
        <v-icon icon="mdi-fire" color="primary" size="56" class="mb-5" />
        <h2 class="text-h4 font-weight-bold text-white mb-3">Resume Roaster</h2>
        <p class="text-body-1" style="color: rgba(255,255,255,0.7); max-width: 340px;">
          AI-powered match scoring, keyword analysis, bullet rewrites, and cover letters — in seconds.
        </p>
        <div class="mt-10 d-flex flex-column" style="gap: 16px;">
          <div v-for="item in brandPoints" :key="item" class="d-flex align-center" style="gap: 10px;">
            <v-icon icon="mdi-check-circle" color="primary" size="20" />
            <span class="text-body-2" style="color: rgba(255,255,255,0.8);">{{ item }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Form panel -->
    <div class="auth-form d-flex align-center justify-center pa-6">
      <div style="width: 100%; max-width: 400px;">
        <!-- Mobile logo -->
        <div class="d-flex d-md-none align-center mb-6" style="gap: 8px;">
          <v-icon icon="mdi-fire" color="primary" size="28" />
          <span class="text-h6 font-weight-bold">Resume Roaster</span>
        </div>

        <h1 class="text-h5 font-weight-bold mb-1">Welcome back</h1>
        <p class="text-body-2 text-medium-emphasis mb-6">Sign in to your account</p>

        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>

        <GoogleSignInButton
          v-if="googleClientId"
          :client-id="googleClientId"
          class="mb-4"
          @credential="handleGoogleCredential"
          @error="handleGoogleError"
        />
        <div v-if="googleClientId" class="d-flex align-center mb-4">
          <v-divider /><span class="text-body-2 text-medium-emphasis px-3">or</span><v-divider />
        </div>

        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            required
            prepend-inner-icon="mdi-email"
            class="mb-3"
          />
          <v-text-field
            v-model="password"
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            required
            prepend-inner-icon="mdi-lock"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
            class="mb-4"
          />
          <div v-if="turnstileSiteKey" ref="turnstileRef" class="mb-4"></div>
          <v-btn type="submit" color="primary" block size="large" :loading="loading" :disabled="turnstileSiteKey && !turnstileToken">
            Sign in
          </v-btn>
        </v-form>

        <div class="text-center mt-6">
          <span class="text-body-2 text-medium-emphasis">No account?</span>
          <v-btn variant="text" size="small" to="/register" color="primary">Register</v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'

useHead({
  title: 'Sign In - Resume Roaster',
  meta: [
    { name: 'description', content: 'Sign in to Resume Roaster to access AI-powered resume analysis, ATS checking, and cover letter generation.' },
    { property: 'og:title', content: 'Sign In - Resume Roaster' },
    { property: 'og:url', content: 'https://resume-roaster.com/login' },
  ],
  link: [
    { rel: 'canonical', href: 'https://resume-roaster.com/login' },
  ],
})

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref(null)

const googleClientId = ref('')
const turnstileSiteKey = ref('')
const turnstileToken = ref('')
const turnstileRef = ref(null)
let turnstileWidgetId = null

const brandPoints = computed(() => {
  const points = ['Results in under 30 seconds', '7 AI-powered tools']
  if (auth.paymentsEnabled) {
    points.unshift('1 free credit on signup', 'No credit card required')
  }
  return points
})

onMounted(async () => {
  try {
    const { data } = await authApi.getConfig()
    turnstileSiteKey.value = data.cloudflare_turnstile_site_key || ''
    googleClientId.value = data.google_oauth_client_id || ''
  } catch {
    turnstileSiteKey.value = ''
    googleClientId.value = ''
  }

  if (turnstileSiteKey.value) {
    await waitForTurnstile()
    renderTurnstile()
  }
})

function waitForTurnstile() {
  return new Promise((resolve) => {
    if (window.turnstile) return resolve()
    const interval = setInterval(() => {
      if (window.turnstile) {
        clearInterval(interval)
        resolve()
      }
    }, 100)
  })
}

function renderTurnstile() {
  if (!turnstileRef.value || !window.turnstile) return
  turnstileWidgetId = window.turnstile.render(turnstileRef.value, {
    sitekey: turnstileSiteKey.value,
    theme: 'light',
    callback: (token) => { turnstileToken.value = token },
    'expired-callback': () => { turnstileToken.value = '' },
    'error-callback': () => { turnstileToken.value = '' },
  })
}

function resetTurnstile() {
  turnstileToken.value = ''
  if (window.turnstile && turnstileWidgetId != null) {
    window.turnstile.reset(turnstileWidgetId)
  }
}

async function handleGoogleCredential(credential) {
  loading.value = true
  error.value = null
  try {
    await auth.googleLogin(credential)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Google sign-in failed.'
  } finally {
    loading.value = false
  }
}

function handleGoogleError(msg) {
  error.value = 'Google sign-in unavailable.'
}

async function submit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(email.value, password.value, turnstileToken.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid credentials.'
    resetTurnstile()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-layout {
  min-height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.auth-brand {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 50%, #0f3460 100%);
}

@media (max-width: 960px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }
}
</style>
