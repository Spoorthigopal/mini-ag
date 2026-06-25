import { useState, useCallback } from 'react';
import api from '../services/api';

export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
}

export const useApi = <T>(
  apiCall: (...args: any[]) => Promise<any>
): UseApiResult<T> => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiCall(...args);
        setData(response.data);
        return response.data;
      } catch (err: any) {
        const errMsg = err.response?.data?.message || err.message || 'An unexpected error occurred.';
        setError(errMsg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiCall]
  );

  return {
    data,
    loading,
    error,
    execute,
  };
};

export default useApi;
