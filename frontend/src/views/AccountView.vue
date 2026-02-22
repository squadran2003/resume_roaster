<template>
  <v-container class="py-8 d-flex justify-center">
    <v-card width="520" elevation="4" rounded="lg">
      <v-card-title class="pt-6 text-h5 font-weight-bold">Account</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-alert v-if="saved" type="success" density="compact" class="mb-4">Changes saved.</v-alert>

        <v-list lines="two">
          <v-list-item prepend-icon="mdi-email" title="Email" :subtitle="auth.user?.email || '—'" />
          <v-list-item
            prepend-icon="mdi-star"
            title="Plan"
            :subtitle="auth.user?.profile?.subscription_tier || 'Free'"
          />
          <v-list-item
            prepend-icon="mdi-currency-usd"
            title="Credits"
            :subtitle="String(auth.user?.profile?.credits_remaining ?? 0)"
          />
        </v-list>

        <v-divider class="my-4" />

        <h3 class="text-subtitle-1 font-weight-bold mb-3">Change password</h3>
        <v-form ref="formRef" @submit.prevent="changePassword">
          <v-text-field
            v-model="newPassword"
            label="New password"
            type="password"
            variant="outlined"
            class="mb-3"
          />
          <v-text-field
            v-model="newPassword2"
            label="Confirm new password"
            type="password"
            variant="outlined"
            class="mb-4"
          />
          <v-btn type="submit" color="primary" :loading="saving">Save changes</v-btn>
        </v-form>

        <v-divider class="my-6" />
        <v-btn
          color="error"
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="auth.logout"
        >
          Sign out
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api/auth'

const auth = useAuthStore()
const formRef = ref(null)
const newPassword = ref('')
const newPassword2 = ref('')
const saving = ref(false)
const error = ref(null)
const saved = ref(false)

async function changePassword() {
  if (newPassword.value !== newPassword2.value) {
    error.value = 'Passwords do not match.'
    return
  }
  saving.value = true
  error.value = null
  saved.value = false
  try {
    await authApi.updateMe({ password: newPassword.value, password2: newPassword2.value })
    saved.value = true
    newPassword.value = ''
    newPassword2.value = ''
    formRef.value?.reset()
  } catch (e) {
    const data = e.response?.data
    error.value = data ? Object.values(data).flat().join(' ') : 'Failed to save.'
  } finally {
    saving.value = false
  }
}
</script>
