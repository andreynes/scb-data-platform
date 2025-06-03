// frontend/src/services/apiClient.ts
// ВАЖНО: Этот файл может не использоваться напрямую сгенерированным клиентом.
// Его основная роль - служить источником конфигурации и, возможно,
// для кастомных запросов, не покрываемых генератором.

import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
// Предполагается, что store экспортируется для доступа к состоянию,
// или используется localStorage напрямую.
// import { store } from '../app/store'; // Пример, если Redux store используется для токена/логаута
// import { logoutAction } from '../features/auth/slice'; // Пример logout action

// Базовый URL API из переменных окружения Vite
// ВАЖНО: Убедись, что VITE_API_BASE_URL определена в твоем .env файле (например, VITE_API_BASE_URL=http://localhost:8000)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
// Префикс API из настроек (если settings доступны или захардкожены для фронта)
// В идеале, это тоже должно быть из переменных окружения Vite
const API_V1_PREFIX = '/api/v1'; // Пример, должно быть согласовано

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor (Для информации, как это могло бы работать.
// С openapi-typescript-codegen токен обычно управляется через OpenAPI.TOKEN)
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Пример получения токена из localStorage
    const token = localStorage.getItem('authToken');
    if (token && config.headers) {
      // Исключаем добавление токена для публичных эндпоинтов
      // (необходимо поддерживать список или использовать другую логику)
      const publicPaths = ['/token', '/register']; // Пример
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

// Response Interceptor (Глобальная обработка 401)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Предотвращение бесконечного цикла для 401

      console.error('Unauthorized access - 401! Logging out.');
      // Логика логаута:
      // 1. Очистить токен
      localStorage.removeItem('authToken');
      // 2. Диспатч Redux action (если используется Redux для состояния аутентификации)
      // store.dispatch(logoutAction());
      // 3. Перенаправление на страницу логина
      // window.location.href = '/login'; // Простой редирект

      // Важно: если вы пытаетесь обновить токен (refresh token), логика будет здесь.
      // Для MVP просто логаут.
    }
    return Promise.reject(error);
  }
);

export default apiClient;