// frontend/src/pages/LoginPage.tsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginForm } from '../features/auth/components/LoginForm'; // <-- ИСПРАВЛЕННЫЙ ПУТЬ
import { useAuth } from '../features/auth/hooks/useAuth'; // <-- ИСПРАВЛЕННЫЙ ПУТЬ
import { LoginFormData } from '../features/auth/types'; // <-- ИСПРАВЛЕННЫЙ ПУТЬ
import { useAppSelector } from '../app/hooks'; // <-- Добавил для проверки статуса
import { selectIsAuthenticated } from '../features/auth/slice'; // <-- Добавил для проверки статуса

const LoginPage: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  useEffect(() => {
    // Если пользователь уже залогинен, перенаправляем его с этой страницы
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);


  const handleLoginSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
      // После успешного вызова login, useEffect выше должен будет сработать и перенаправить
    } catch (err) {
      // Ошибка будет обработана и отображена через 'error' из хука useAuth
      console.error("Login failed on page:", err);
    }
  };
  
  return (
    <LoginForm 
      onSubmit={handleLoginSubmit} 
      isLoading={isLoading} 
      error={error} 
    />
  );
};

export default LoginPage;