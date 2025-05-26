import '@/assets/styles/global/fonts.scss'
import '@/assets/styles/main.scss'
import {createApp, h, provide} from 'vue'
import { DefaultApolloClient } from '@vue/apollo-composable'
import { createApolloClient } from './apollo'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import {setupI18n} from "@/core/plugins/i18n.config.js";
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

const pinia = createPinia()
const i18n = await setupI18n()

const app = createApp({
  setup() {
    const apolloClient = createApolloClient()

    provide(DefaultApolloClient, apolloClient)
  },
  render: () => h(App)
})

app
    .use(pinia)
    .use(i18n)
    .use(router)
    .use(ElementPlus)

app.mount('#app')