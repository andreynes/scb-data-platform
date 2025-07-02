import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { store } from '../app/store';
// === КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ===
// Импортируем logoutAction вместо logout
import { logoutAction } from '../features/auth/slice';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor для добавления токена
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('authToken');
    if (token && config.headers) {
      const publicPaths = ['/token'];
      if (!publicPaths.some(path => config.url?.includes(path))) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor для глобальной обработки ошибок 401
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      console.error('Unauthorized access - 401! Logging out via apiClient interceptor.');
      
      // === КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ===
      // Диспатчим правильное действие
      store.dispatch(logoutAction());
      
      // Перенаправление можно убрать отсюда, если оно есть в компонентах,
      // но для надежности можно оставить.
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;