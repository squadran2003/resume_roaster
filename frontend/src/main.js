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
  theme: { defaultTheme: 'light' },
})

const head = createHead()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(head)
app.mount('#app')
