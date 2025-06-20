// frontend/src/features/auth/hooks/useAuth.ts
import { useCallback, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../../../app/hooks';
import { 
  loginUser, 
  fetchUserMe,
  logout as logoutAction,
  selectIsAuthenticated, 
  selectCurrentUser, 
  selectAuthIsLoading, 
  selectAuthError 
} from '../slice';
import type { LoginFormData, AuthHookResult } from '../types';
import { authApi } from '../../../services';

export function useAuth(): AuthHookResult {
  const dispatch = useAppDispatch();

  // Получаем данные из Redux store с помощью селекторов
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const user = useAppSelector(selectCurrentUser);
  const isLoading = useAppSelector(selectAuthIsLoading);
  const error = useAppSelector(selectAuthError);

  // Функция для входа в систему
  const login = useCallback(
    async (credentials: LoginFormData) => {
      // Диспатчим thunk, который выполнит API-запрос и обработает результат
      // .unwrap() поможет пробросить ошибку, если она произойдет, чтобы ее можно было поймать в компоненте
      await dispatch(loginUser(credentials)).unwrap();
    },
    [dispatch]
  );

  // Функция для выхода из системы
  const logout = useCallback(() => {
    // Диспатчим action, который очистит состояние и токен
    dispatch(logoutAction());
  }, [dispatch]);

  // Эффект для автоматической загрузки данных пользователя при наличии токена
  useEffect(() => {
    // Если есть токен, но нет данных о пользователе и не идет загрузка
    if (localStorage.getItem('authToken') && !user && !isLoading) {
      dispatch(fetchUserMe());
    }
  }, [dispatch, user, isLoading]);
  
  // Возвращаем состояние и функции для использования в компонентах
  return {
    isAuthenticated,
    user,
    isLoading,
    error,
    login,
    logout,
  };
}