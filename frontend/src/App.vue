<template>
  <v-app>
    <v-app-bar color="primary" elevation="2">
      <v-app-bar-title>
        <router-link to="/" class="text-white text-decoration-none font-weight-bold">
          Resume Roaster
        </router-link>
      </v-app-bar-title>
      <template v-if="auth.isAuthenticated">
        <v-btn to="/dashboard" variant="text" color="white">Dashboard</v-btn>
        <v-btn to="/upload" variant="text" color="white">Upload</v-btn>
        <v-btn to="/account" variant="text" color="white">Account</v-btn>
        <v-btn @click="auth.logout" variant="text" color="white" prepend-icon="mdi-logout">
          Sign out
        </v-btn>
      </template>
      <template v-else>
        <v-btn to="/login" variant="text" color="white">Login</v-btn>
        <v-btn to="/register" variant="outlined" color="white" class="mr-2">Register</v-btn>
      </template>
      <v-btn
        :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        variant="text"
        color="white"
        @click="toggleTheme"
        :title="theme.global.current.value.dark ? 'Switch to light mode' : 'Switch to dark mode'"
      />
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const theme = useTheme()

function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
  localStorage.setItem('theme', theme.global.name.value)
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    theme.global.name.value = saved
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    theme.global.name.value = 'dark'
  }
})
</script>
