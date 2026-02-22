<template>
  <v-container class="d-flex align-center justify-center" style="min-height: 80vh">
    <v-card width="420" elevation="4" rounded="lg">
      <v-card-title class="pt-6 pb-2 text-center text-h5 font-weight-bold">Sign in</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="email"
            label="Email"
            type="email"
            required
            prepend-inner-icon="mdi-email"
            variant="outlined"
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
            variant="outlined"
            class="mb-4"
          />
          <v-btn type="submit" color="primary" block size="large" :loading="loading">
            Sign in
          </v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center pb-6">
        <span class="text-body-2">No account?</span>
        <v-btn variant="text" size="small" to="/register" color="primary">Register</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref(null)

async function submit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid credentials.'
  } finally {
    loading.value = false
  }
}
</script>
