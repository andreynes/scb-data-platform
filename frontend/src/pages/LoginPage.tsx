// frontend/src/pages/LoginPage.tsx

import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginForm } from '../features/auth/components/LoginForm';
import { useAuth } from '../features/auth/hooks/useAuth';
import { LoginFormData } from '../features/auth/types';
import { useAppSelector } from '../app/hooks';
import { selectIsAuthenticated } from '../features/auth/slice';

const LoginPage: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLoginSubmit = useCallback(
    async (data: LoginFormData) => {
      try {
        await login(data);
      } catch (err) {
        // Ошибка уже обрабатывается в slice, здесь можно не логировать
      }
    },
    [login]
  );

  return <LoginForm onSubmit={handleLoginSubmit} isLoading={isLoading} error={error} />;
};

export default LoginPage;