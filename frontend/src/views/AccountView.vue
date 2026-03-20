<template>
  <v-container class="py-8 d-flex justify-center">
    <div style="width: 100%; max-width: 520px;">
      <h1 class="text-h5 font-weight-bold mb-6">Account</h1>

      <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
      <v-alert v-if="saved" type="success" density="compact" class="mb-4">Changes saved.</v-alert>

      <!-- Profile info -->
      <v-card elevation="0" class="mb-6 section-card">
        <v-list lines="two">
          <v-list-item prepend-icon="mdi-email" title="Email" :subtitle="auth.user?.email || '—'" />
          <v-list-item
            v-if="auth.paymentsEnabled"
            prepend-icon="mdi-star-circle"
            title="Credits"
            :subtitle="`${auth.user?.profile?.credits_remaining ?? 0} remaining`"
          />
        </v-list>
        <div v-if="auth.paymentsEnabled" class="px-4 pb-4">
          <v-btn color="primary" variant="tonal" prepend-icon="mdi-plus" to="/dashboard">
            Buy More Credits
          </v-btn>
        </div>
      </v-card>

      <!-- Change password -->
      <v-card elevation="0" class="mb-6 section-card pa-5">
        <h3 class="text-subtitle-1 font-weight-bold mb-4">Change password</h3>
        <v-form ref="formRef" @submit.prevent="changePassword">
          <v-text-field
            v-model="newPassword"
            label="New password"
            type="password"
            prepend-inner-icon="mdi-lock"
            class="mb-3"
          />
          <v-text-field
            v-model="newPassword2"
            label="Confirm new password"
            type="password"
            prepend-inner-icon="mdi-lock-check"
            class="mb-4"
          />
          <v-btn type="submit" color="primary" :loading="saving">Save changes</v-btn>
        </v-form>
      </v-card>

      <!-- Sign out -->
      <v-card elevation="0" class="section-card pa-5">
        <v-btn
          color="error"
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="auth.logout"
        >
          Sign out
        </v-btn>
      </v-card>
    </div>
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

<style scoped>
.section-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
