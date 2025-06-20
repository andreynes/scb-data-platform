// frontend/src/services/apiClient.ts
import axios from 'axios';
import { store } from '../app/store'; // Импортируем store
import { logout } from '../features/auth/slice'; // <-- ИСПРАВЛЕННЫЙ ИМПОРТ 'logout' вместо 'logoutAction'

// ... (создание apiClient, как в документации) ...
const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api/v1', // Убедитесь, что URL верный
});

// ... (Request Interceptor для токена) ...
apiClient.interceptors.request.use(
  (config) => {
    const token = store.getState().auth.token;
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor для глобальной обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Глобальная обработка ошибки 401 Unauthorized
    if (error.response?.status === 401) {
      console.error('Unauthorized access - 401! Logging out.');
      // Диспатчим action для выхода из системы
      store.dispatch(logout()); 
    }
    return Promise.reject(error);
  }
);

export default apiClient;