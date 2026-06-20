import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createUnhead, headSymbol } from '@unhead/vue'
import App from './App.vue'
import router from './router'

import './assets/variables.css'
import './assets/global.css'

const app = createApp(App)
const pinia = createPinia()
const head = createUnhead()

app.use(pinia)
app.use(router)
app.provide(headSymbol, head)

app.mount('#app')
