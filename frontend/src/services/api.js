import axios from 'axios'

// Central Axios instance. Vite proxies /api -> FastAPI (see vite.config.js).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 4000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err),
)

export default api
