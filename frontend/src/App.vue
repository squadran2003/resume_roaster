<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar color="secondary" elevation="0" class="app-bar-blur">
      <v-app-bar-nav-icon
        class="d-md-none"
        color="white"
        @click="drawer = !drawer"
        aria-label="Toggle navigation menu"
      />
      <v-app-bar-title>
        <router-link to="/" class="text-white text-decoration-none font-weight-bold d-flex align-center" style="gap: 8px; width: fit-content;">
          <v-icon icon="mdi-fire" color="primary" size="28" />
          <span>Resume Roaster</span>
        </router-link>
      </v-app-bar-title>

      <!-- Desktop nav -->
      <template v-if="auth.isAuthenticated" class="d-none d-md-flex">
        <v-btn to="/dashboard" variant="text" color="white" class="d-none d-md-flex">Dashboard</v-btn>
        <v-btn to="/upload" variant="text" color="white" class="d-none d-md-flex">Upload</v-btn>
        <v-btn to="/account" variant="text" color="white" class="d-none d-md-flex">Account</v-btn>
        <v-btn @click="auth.logout" variant="text" color="white" prepend-icon="mdi-logout" class="d-none d-md-flex">
          Sign out
        </v-btn>
      </template>
      <template v-else>
        <v-btn to="/login" variant="text" color="white" class="d-none d-md-flex">Login</v-btn>
        <v-btn to="/register" variant="flat" color="primary" class="d-none d-md-flex mr-2">Get Started</v-btn>
      </template>
      <v-btn
        :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        variant="text"
        color="white"
        @click="toggleTheme"
        :aria-label="theme.global.current.value.dark ? 'Switch to light mode' : 'Switch to dark mode'"
      />
    </v-app-bar>

    <!-- Mobile drawer -->
    <v-navigation-drawer v-model="drawer" temporary location="left" class="d-md-none">
      <v-list nav>
        <v-list-item class="mb-2">
          <template #prepend>
            <v-icon icon="mdi-fire" color="primary" />
          </template>
          <v-list-item-title class="font-weight-bold">Resume Roaster</v-list-item-title>
        </v-list-item>
        <v-divider class="mb-2" />
        <template v-if="auth.isAuthenticated">
          <v-list-item to="/dashboard" prepend-icon="mdi-view-dashboard" title="Dashboard" @click="drawer = false" />
          <v-list-item to="/upload" prepend-icon="mdi-upload" title="Upload Resume" @click="drawer = false" />
          <v-list-item to="/analysis/new" prepend-icon="mdi-robot" title="New Analysis" @click="drawer = false" />
          <v-list-item to="/linkedin" prepend-icon="mdi-linkedin" title="LinkedIn" @click="drawer = false" />
          <v-list-item to="/account" prepend-icon="mdi-account-circle" title="Account" @click="drawer = false" />
          <v-divider class="my-2" />
          <v-list-item prepend-icon="mdi-logout" title="Sign out" @click="auth.logout(); drawer = false" />
        </template>
        <template v-else>
          <v-list-item to="/login" prepend-icon="mdi-login" title="Login" @click="drawer = false" />
          <v-list-item to="/register" prepend-icon="mdi-account-plus" title="Register" @click="drawer = false" />
        </template>
      </v-list>
    </v-navigation-drawer>

    <!-- Main content with page transitions -->
    <v-main>
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </Transition>
      </RouterView>
    </v-main>

    <!-- Global snackbar -->
    <v-snackbar v-model="snackbar.show" :timeout="2000" location="bottom right" color="surface" rounded="lg">
      <div class="d-flex align-center" style="gap: 8px;">
        <v-icon icon="mdi-check-circle" color="success" size="20" />
        {{ snackbar.message }}
      </div>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, reactive, onMounted, provide } from 'vue'
import { useTheme } from 'vuetify'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const theme = useTheme()
const drawer = ref(false)

// Global snackbar
const snackbar = reactive({ show: false, message: '' })
function notify(msg) {
  snackbar.message = msg
  snackbar.show = true
}
provide('notify', notify)

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

<style>
/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* App bar glass effect */
.app-bar-blur .v-toolbar__content {
  backdrop-filter: blur(12px);
}
</style>
