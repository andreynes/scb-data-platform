// frontend/src/app/router.tsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAppSelector } from './hooks';
import { selectIsAuthenticated, selectCurrentUser } from '../features/auth/slice';

// --- ИМПОРТЫ СТРАНИЦ ---
import LoginPage from '../pages/LoginPage';
import DataExplorerPage from '../pages/DataExplorerPage';
import UserProfilePage from '../pages/UserProfilePage';
import NotFoundPage from '../pages/NotFoundPage';
// Административные страницы
import OntologyManagementPage from '../pages/OntologyManagementPage';
import VerificationPage from '../pages/VerificationPage';

// --- ИМПОРТЫ МАКЕТОВ ---
import MainLayout from '../components/Layout/MainLayout';
import AuthLayout from '../components/Layout/AuthLayout';

// Компонент для защиты роутов (остается без изменений)
const ProtectedRoute = ({ children, adminOnly = false }: { children: JSX.Element; adminOnly?: boolean }) => {
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const currentUser = useAppSelector(selectCurrentUser);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && currentUser?.role !== 'admin' && currentUser?.role !== 'maintainer') {
    return <Navigate to="/" replace />;
  }

  return children;
};

export function AppRouter() {
  return (
    <Routes>
      {/* Маршруты для аутентификации, использующие AuthLayout */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Маршруты, требующие аутентификации и использующие MainLayout */}
      <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        
        {/* Главная страница для залогиненных пользователей */}
        <Route index element={<DataExplorerPage />} />
        
        {/* Основные страницы для всех пользователей */}
        <Route path="data-explorer" element={<DataExplorerPage />} />
        <Route path="profile" element={<UserProfilePage />} />

        {/* 
          --- АДМИНИСТРАТИВНЫЕ МАРШРУТЫ ---
          Они также являются дочерними для MainLayout, чтобы сохранить общую навигацию.
          Каждый из них защищен флагом adminOnly.
        */}
        <Route 
          path="ontology" 
          element={<ProtectedRoute adminOnly><OntologyManagementPage /></ProtectedRoute>} 
        />
        <Route 
          path="verification" 
          element={<ProtectedRoute adminOnly><VerificationPage /></ProtectedRoute>} 
        />
        {/* Если в будущем появится общая админ-панель, ее можно будет добавить сюда: */}
        {/* <Route path="admin" element={<ProtectedRoute adminOnly><AdminDashboardPage /></ProtectedRoute>} /> */}

      </Route>

      {/* Страница "Не найдено" для всех остальных путей */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}