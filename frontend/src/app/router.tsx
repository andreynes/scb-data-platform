// frontend/src/app/router.tsx
import React, { Suspense } from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Spin } from 'antd';

// --- Прямые импорты страниц ---
// import LoginPageDirect from '../pages/LoginPage'; // Если/когда будет готова
import OntologyManagementPageDirect from '../pages/OntologyManagementPage';
import FileUploadPageDirect from '../pages/FileUploadPage'; // <-- ДОБАВЛЕН ИМПОРТ

// --- Ленивая загрузка (если будете использовать позже) ---
// const VerificationPage = React.lazy(() => import('../pages/VerificationPage'));
// const UserProfilePage = React.lazy(() => import('../pages/UserProfilePage'));
// const AdminDashboardPage = React.lazy(() => import('../pages/AdminDashboardPage'));
// const NotFoundPage = React.lazy(() => import('../pages/NotFoundPage'));
// const DataExplorerPage = React.lazy(() => import('../pages/DataExplorerPage'));


// --- Компоненты Макетов (Layouts) ---
const MainLayout: React.FC = () => (
  <div style={{ padding: '20px' }}>
    {/* Здесь может быть шапка, боковое меню и т.д. */}
    <Outlet /> {/* Сюда будут рендериться дочерние маршруты */}
  </div>
);

const AuthLayout: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
    <Outlet />
  </div>
);

// --- Компонент для Защищенных Маршрутов (ЗАГЛУШКА для MVP) ---
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
  // Для MVP можно пока упростить проверку ролей, если функционал админа еще не разделен четко
  if (adminOnly && userRole !== 'admin' && userRole !== 'maintainer') {
    console.warn('ProtectedRoute: Admin access denied, redirecting.'); // Лог для отладки
    return <Navigate to="/" replace />;
  }
  return children;
};


export function AppRouter() {
  return (
    <Suspense fallback={<Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />}>
      <Routes>
        {/* Маршруты, использующие MainLayout */}
        <Route
          path="/"
          element={
            <ProtectedRoute> {/* Защищаем все маршруты внутри MainLayout */}
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Главная страница после логина - теперь это /upload */}
          <Route index element={<Navigate to="/upload" replace />} />
          
          <Route 
            path="upload" // <-- НОВЫЙ МАРШРУТ ДЛЯ ЗАГРУЗКИ
            element={<FileUploadPageDirect />} 
          />
          
          {/* Ваша страница управления онтологией (оставил adminOnly для примера) */}
          <Route 
            path="ontology-management" 
            element={
              <ProtectedRoute adminOnly> {/* Пример защиты админского раздела */}
                <OntologyManagementPageDirect />
              </ProtectedRoute>
            }
          />
          
          {/* Другие потенциальные маршруты (заглушки или реальные) */}
          {/* <Route path="data-explorer" element={<DataExplorerPage />} /> */}
          {/* <Route path="profile" element={<UserProfilePage />} /> */}
          {/* <Route path="admin/verification" element={<VerificationPage />} /> */}
          {/* <Route path="admin/dashboard" element={<AdminDashboardPage />} /> */}
        </Route>

        {/* Маршруты, использующие AuthLayout (например, для логина) */}
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