// frontend/src/features/auth/hooks/useAuth.ts

import { useCallback, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../../../app/hooks';
import {
  selectIsAuthenticated,
  selectCurrentUser,
  selectAuthIsLoading,
  selectAuthError,
  loginUser,
  fetchInitialUser,
  logoutAction,
} from '../slice';
import type { LoginCredentials } from '../../../services/generated';

export function useAuth() {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const user = useAppSelector(selectCurrentUser);
  const isLoading = useAppSelector(selectAuthIsLoading);
  const error = useAppSelector(selectAuthError);

  const login = useCallback(
    (credentials: LoginCredentials) => {
      return dispatch(loginUser(credentials)).unwrap();
    },
    [dispatch]
  );

  const logout = useCallback(() => {
    dispatch(logoutAction());
  }, [dispatch]);

  // Этот useEffect теперь нужен только для первоначальной загрузки при обновлении страницы
  useEffect(() => {
    if (!user) {
      dispatch(fetchInitialUser());
    }
  }, [dispatch, user]);

  return { isAuthenticated, user, isLoading, error, login, logout };
}