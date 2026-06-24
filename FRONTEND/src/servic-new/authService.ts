import axios, { AxiosResponse } from 'axios';

// Helper to get the base API URL from Vite env or default
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Store JWT token in localStorage
 */
export const setToken = (token: string): void => {
  localStorage.setItem('token', token);
};

/** Retrieve JWT token */
export const getToken = (): string | null => {
  return localStorage.getItem('token');
};

/** Check if a user is authenticated */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token;
};

/** Logout user – clear token */
export const logout = (): void => {
  localStorage.removeItem('token');
};

/** Login request */
export const login = async (
  email: string,
  password: string
): Promise<AxiosResponse<any>> => {
  const response = await axios.post(`${baseURL}/auth/login`, {
    email,
    password,
  });
  // Assuming the API returns a JWT token in response.data.token
  if (response.data?.token) {
    setToken(response.data.token);
  }
  return response;
};

/** Register request */
export const register = async (
  email: string,
  password: string
): Promise<AxiosResponse<any>> => {
  const response = await axios.post(`${baseURL}/auth/register`, {
    email,
    password,
  });
  // If registration also returns a token, store it
  if (response.data?.token) {
    setToken(response.data.token);
  }
  return response;
};
