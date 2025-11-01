import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './components/Home.vue'
import AnalysisResult from './components/AnalysisResult.vue'
import './style.css'

const routes = [
  { path: '/', component: Home },
  { path: '/analysis', component: AnalysisResult }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
