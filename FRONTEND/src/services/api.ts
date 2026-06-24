// Axios API Instance with Interceptors
// Generated from Prompt 4

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Interceptors configured here

export default api
