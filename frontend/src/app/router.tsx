// frontend/src/app/router.tsx
import React, { Suspense } from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Spin } from 'antd';

// --- Прямые импорты страниц ---
// import LoginPageDirect from '../pages/LoginPage'; // Если/когда будет готова
import OntologyManagementPageDirect from '../pages/OntologyManagementPage';
import FileUploadPageDirect from '../pages/FileUploadPage';
import DataExplorerPage from '../pages/DataExplorerPage'; // <-- НАША НОВАЯ СТРАНИЦА

// --- Ленивая загрузка (можно будет использовать позже для других страниц) ---
// const VerificationPage = React.lazy(() => import('../pages/VerificationPage'));
// const UserProfilePage = React.lazy(() => import('../pages/UserProfilePage'));
// const AdminDashboardPage = React.lazy(() => import('../pages/AdminDashboardPage'));
// const NotFoundPage = React.lazy(() => import('../pages/NotFoundPage'));


// --- Компоненты Макетов (Layouts) ---
const MainLayout: React.FC = () => (
  <div style={{ padding: '20px' }}> {/* Пример базового макета */}
    {/* Здесь может быть шапка, боковое меню, навигация и т.д. */}
    <Outlet /> {/* Сюда будут рендериться дочерние маршруты */}
  </div>
);

const AuthLayout: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
    <Outlet />
  </div>
);

// --- Компонент для Защищенных Маршрутов (ВАША ЗАГЛУШКА) ---
interface ProtectedRouteProps {
  children: JSX.Element;
  adminOnly?: boolean;
}
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, adminOnly }) => {
  const isAuthenticated = true; // ЗАГЛУШКА: Пользователь всегда аутентифицирован
  const userRole = 'admin';   // ЗАГЛУШКА: У пользователя всегда роль админа

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && userRole !== 'admin' && userRole !== 'maintainer') {
    console.warn('ProtectedRoute: Admin/Maintainer access denied, redirecting to data explorer.');
    return <Navigate to="/data-explorer" replace />; // Перенаправляем на главную для обычных пользователей
  }
  return children;
};


export function AppRouter() {
  return (
    <Suspense fallback={<Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />}>
      <Routes>
        {/* Маршруты, использующие MainLayout (для аутентифицированных пользователей) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Главная страница после логина - теперь это /data-explorer */}
          <Route index element={<Navigate to="/data-explorer" replace />} />
          
          <Route 
            path="upload"
            element={<FileUploadPageDirect />} 
          />
          
          {/* СТРАНИЦА ИССЛЕДОВАТЕЛЯ ДАННЫХ */}
          <Route 
            path="data-explorer" 
            element={<DataExplorerPage />} 
          />
          
          <Route 
            path="ontology-management" 
            element={
              <ProtectedRoute adminOnly>
                <OntologyManagementPageDirect />
              </ProtectedRoute>
            }
          />
          
          {/* Другие защищенные маршруты */}
          {/* <Route path="profile" element={<UserProfilePage />} /> */}
          {/* <Route path="admin/verification" element={<ProtectedRoute adminOnly><VerificationPage /></ProtectedRoute>} /> */}
          {/* <Route path="admin/dashboard" element={<ProtectedRoute adminOnly><AdminDashboardPage /></ProtectedRoute>} /> */}
        </Route>

        {/* Маршруты для аутентификации (например, логин), использующие AuthLayout */}
        <Route element={<AuthLayout />}>
          {/* <Route path="/login" element={<LoginPageDirect />} /> */}
           <Route path="/login" element={<div>Страница Логина (заглушка)</div>} />
        </Route>

        {/* Страница "Не найдено" (404) */}
        {/* <Route path="*" element={<NotFoundPage />} /> */}
        <Route path="*" element={<div>404 - Страница не найдена (заглушка)</div>} />
      </Routes>
    </Suspense>
  );
}