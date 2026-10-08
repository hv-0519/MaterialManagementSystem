import { createApp } from 'vue'
import '@fontsource-variable/inter'
import './assets/styles/base.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

router.isReady().then(() => {
  app.mount('#app')
})
