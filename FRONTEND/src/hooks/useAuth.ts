import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import * as authService from '../services/authService';
import { login as loginAction, logout as logoutAction, setLoading } from '../redux/slices/authSlice';

export const useAuth = () => {
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      dispatch(setLoading(true));
      const response = await authService.login(email, password);
      const { user, token } = response.data;
      
      dispatch(loginAction({ user, token }));
      navigate('/');
      return true;
    } catch (err: any) {
      const errMsg = err.response?.data?.message || 'Invalid email or password.';
      setError(errMsg);
      dispatch(setLoading(false));
      return false;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      setError(null);
      dispatch(setLoading(true));
      const response = await authService.register(email, password);
      const { user, token } = response.data;
      
      dispatch(loginAction({ user, token }));
      navigate('/');
      return true;
    } catch (err: any) {
      const errMsg = err.response?.data?.message || 'Registration failed. Please try again.';
      setError(errMsg);
      dispatch(setLoading(false));
      return false;
    }
  };

  const logout = () => {
    authService.logout();
    dispatch(logoutAction());
    navigate('/login');
  };

  return {
    login,
    register,
    logout,
    error,
  };
};

export default useAuth;
