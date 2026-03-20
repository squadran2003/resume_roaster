<template>
  <v-container class="d-flex align-center justify-center" style="min-height: 80vh">
    <v-card width="420" elevation="4" rounded="lg">
      <v-card-title class="pt-6 pb-2 text-center text-h5 font-weight-bold">Create account</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-alert v-if="success" type="success" density="compact" class="mb-4">
          Account created! <router-link to="/login">Sign in</router-link>
        </v-alert>
        <template v-if="!success">
          <GoogleSignInButton
            v-if="googleClientId"
            :client-id="googleClientId"
            class="mb-4"
            @credential="handleGoogleCredential"
            @error="handleGoogleError"
          />
          <div v-if="googleClientId" class="d-flex align-center mb-4">
            <v-divider /><span class="text-body-2 text-grey px-3">or</span><v-divider />
          </div>
        </template>
        <v-form v-if="!success" @submit.prevent="submit">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            required
            variant="outlined"
            prepend-inner-icon="mdi-email"
            class="mb-3"
          />
          <v-text-field
            v-model="password"
            label="Password"
            :type="showPw ? 'text' : 'password'"
            required
            variant="outlined"
            prepend-inner-icon="mdi-lock"
            :append-inner-icon="showPw ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPw = !showPw"
            class="mb-3"
          />
          <v-text-field
            v-model="password2"
            label="Confirm password"
            :type="showPw ? 'text' : 'password'"
            required
            variant="outlined"
            prepend-inner-icon="mdi-lock-check"
            class="mb-4"
          />
          <div v-if="turnstileSiteKey" ref="turnstileRef" class="mb-4"></div>
          <v-btn type="submit" color="primary" block size="large" :loading="loading" :disabled="turnstileSiteKey && !turnstileToken">Register</v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center pb-6">
        <span class="text-body-2">Have an account?</span>
        <v-btn variant="text" size="small" to="/login" color="primary">Sign in</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'
import GoogleSignInButton from '../components/GoogleSignInButton.vue'

useHead({
  title: 'Create Account - Resume Roaster | Free AI Resume Analysis',
  meta: [
    { name: 'description', content: 'Create a free Resume Roaster account. Get 1 free credit to analyze your resume with AI — no credit card required.' },
    { property: 'og:title', content: 'Create Account - Resume Roaster | Free AI Resume Analysis' },
    { property: 'og:url', content: 'https://resume-roaster.com/register' },
  ],
  link: [
    { rel: 'canonical', href: 'https://resume-roaster.com/register' },
  ],
})

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const password2 = ref('')
const showPw = ref(false)
const loading = ref(false)
const error = ref(null)
const success = ref(false)

const googleClientId = ref('')
const turnstileSiteKey = ref('')
const turnstileToken = ref('')
const turnstileRef = ref(null)
let turnstileWidgetId = null

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
  if (password.value !== password2.value) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  error.value = null
  try {
    const payload = { email: email.value, password: password.value, password_confirm: password2.value }
    if (turnstileToken.value) payload.turnstile_token = turnstileToken.value
    await authApi.register(payload)
    success.value = true
  } catch (e) {
    const data = e.response?.data
    error.value = data?.detail || (data ? Object.values(data).flat().join(' ') : 'Registration failed.')
    resetTurnstile()
  } finally {
    loading.value = false
  }
}
</script>
