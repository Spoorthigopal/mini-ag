import axios from 'axios';
import { getToken, logout } from './authService';

// Base URL from Vite env or fallback
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create Axios instance
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Authorization header if token exists
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers = config.headers || {};
      // @ts-ignore – Axios header types
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (401 logout removed to keep user logged in until explicit logout)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Per user requirements, we do not log out on 401
    // if (error.response?.status === 401) {
    //   logout();
    //   if (typeof window !== 'undefined') {
    //     window.location.href = '/login';
    //   }
    // }
    return Promise.reject(error);
  }
);

export default api;
