import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Bundle Vuetify into the SSR/prerender output so Vite transforms its per-component
  // CSS imports; otherwise Node's ESM loader chokes on `.css` during prerender.
  ssr: {
    noExternal: ['vuetify'],
  },
  // Static prerender (vite-ssg): only the public marketing/auth pages get baked
  // to real HTML. Authenticated + dynamic (:id/:token) routes stay client-rendered.
  ssgOptions: {
    script: 'async',
    formatting: 'minify',
    includedRoutes() {
      return [
        '/',
        '/login',
        '/register',
        '/ats-resume-checker',
        '/cover-letter-generator',
        '/resume-keyword-scanner',
      ]
    },
  },
})
