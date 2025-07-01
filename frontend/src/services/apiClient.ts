// frontend/src/services/apiClient.ts
import axios from 'axios';
import { store } from '../app/store';
import { logout } from '../features/auth/slice';

const apiClient = axios.create({
    // --- ИЗМЕНЕНИЕ: Используем относительный путь, Vite проксирует его ---
    baseURL: '/api/v1', 
});

// Request Interceptor для токена (ОСТАВЛЯЕМ, ОН ПРАВИЛЬНЫЙ)
apiClient.interceptors.request.use(
  (config) => {
    // Берем токен из Redux store
    const token = store.getState().auth.token; 
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor для логаута (ОСТАВЛЯЕМ, ОН ПРАВИЛЬНЫЙ)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized access - 401! Logging out.');
      store.dispatch(logout()); 
    }
    return Promise.reject(error);
  }
);

export default apiClient;