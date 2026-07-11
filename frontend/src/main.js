import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import { routes, setupRouterGuards } from './router'

const vuetify = createVuetify({
  ssr: true,
  components,
  directives,
  icons: { defaultSet: 'mdi' },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#E64A19',
          'primary-darken-1': '#BF360C',
          secondary: '#1A1A2E',
          accent: '#FF7043',
          surface: '#FFFFFF',
          background: '#F5F5F7',
          error: '#D32F2F',
          warning: '#F57C00',
          success: '#2E7D32',
          info: '#0288D1',
        },
      },
      dark: {
        colors: {
          primary: '#FF7043',
          'primary-darken-1': '#E64A19',
          secondary: '#16213E',
          accent: '#FFAB91',
          surface: '#1E1E2E',
          background: '#12121F',
          error: '#EF9A9A',
          warning: '#FFCC02',
          success: '#A5D6A7',
          info: '#4FC3F7',
        },
      },
    },
  },
  defaults: {
    VCard: { rounded: 'xl' },
    VBtn: { rounded: 'lg' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VTextarea: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
    VFileInput: { variant: 'outlined', density: 'comfortable' },
  },
})

// ViteSSG bootstraps the app for both the browser and the static prerender.
// It creates the router (from `routes`) and the unhead instance for us.
export const createApp = ViteSSG(
  App,
  { routes },
  ({ app, router }) => {
    app.use(createPinia())
    app.use(vuetify)
    setupRouterGuards(router)
  },
)
