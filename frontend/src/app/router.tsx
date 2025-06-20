// frontend/src/app/router.tsx
import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from './hooks';
import { selectIsAuthenticated } from '../features/auth/slice';

// Импорты страниц
import LoginPage from '../pages/LoginPage';
import DataExplorerPage from '../pages/DataExplorerPage';
import FileUploadPage from '../pages/FileUploadPage'; // <-- Убедитесь, что этот импорт есть
import UserProfilePage from '../pages/UserProfilePage';
import NotFoundPage from '../pages/NotFoundPage';

// Импорты макетов
import MainLayout from '../components/Layout/MainLayout';
import AuthLayout from '../components/Layout/AuthLayout';

// Компонент для защиты роутов
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export function AppRouter() {
  return (
    <Routes>
      {/* Маршруты, требующие аутентификации и использующие основной макет */}
      <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route index element={<DataExplorerPage />} />
        <Route path="data-explorer" element={<DataExplorerPage />} />
        <Route path="upload" element={<FileUploadPage />} /> {/* <-- ВОТ НУЖНЫЙ МАРШРУТ */}
        <Route path="profile" element={<UserProfilePage />} />
        {/* Сюда можно добавлять другие защищенные страницы */}
      </Route>

      {/* Маршруты для аутентификации */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Страница "Не найдено" */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}