import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import { createHead } from '@unhead/vue/client'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
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
          secondary: '#90CAF9',
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

const head = createHead()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(head)
app.mount('#app')
