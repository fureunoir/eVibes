import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  envDir: '../',
  envPrefix: 'EVIBES_',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@core': fileURLToPath(new URL('./src/core', import.meta.url)),
      '@graphql': fileURLToPath(new URL('./src/graphql', import.meta.url)),
      '@styles': fileURLToPath(new URL('./src/assets/styles', import.meta.url)),
      '@icons': fileURLToPath(new URL('./src/assets/icons', import.meta.url)),
      '@images': fileURLToPath(new URL('./src/assets/images', import.meta.url)),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "@/assets/styles/global/variables.scss" as *;
          @use "@/assets/styles/global/mixins.scss" as *;
        `
      }
    }
  },
  build: {
    sourcemap: true,
    target: 'ES2022',
  }
})
