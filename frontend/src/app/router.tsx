// frontend/src/app/router.tsx
import React, { Suspense } from 'react'; // Suspense может понадобиться для ленивой загрузки
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Spin } from 'antd';

// --- Компоненты Макетов (Layouts) ---
// Предположим, у вас будут какие-то компоненты макетов
// Если их пока нет, можно использовать простые div или React.Fragment
// или рендерить страницы напрямую без общего макета для MVP.

// Пример простого MainLayout (позже можно вынести в отдельный файл)
const MainLayout: React.FC = () => (
  <div style={{ padding: '20px' }}>
    {/* Здесь может быть шапка, боковое меню и т.д. */}
    <Outlet /> {/* Сюда будут рендериться дочерние маршруты */}
  </div>
);

// Пример простого AuthLayout (для страниц логина/регистрации)
const AuthLayout: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
    <Outlet />
  </div>
);

// --- Компонент для Защищенных Маршрутов (Заглушка для MVP) ---
// В MVP можно обойтись без реальной защиты, если аутентификация еще не реализована
// или если эндпоинты, к которым обращаются страницы, уже защищены на бэкенде.
// Если аутентификация уже есть, сюда нужно добавить логику проверки токена/статуса из Redux.
interface ProtectedRouteProps {
  children: JSX.Element;
  adminOnly?: boolean; // Пример для ролей
}
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, adminOnly }) => {
  const isAuthenticated = true; // ЗАГЛУШКА: Предполагаем, что пользователь аутентифицирован
  const userRole = 'admin';   // ЗАГЛУШКА: Предполагаем, что у пользователя роль админа

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && userRole !== 'admin' && userRole !== 'maintainer') {
    return <Navigate to="/" replace />; // Или на страницу "Доступ запрещен"
  }
  return children;
};


// --- Ленивая загрузка страниц (опционально, но хорошо для производительности) ---
// Для MVP можно импортировать напрямую, чтобы не усложнять.
// const LoginPage = React.lazy(() => import('../pages/LoginPage'));
// const DataExplorerPage = React.lazy(() => import('../pages/DataExplorerPage'));
const OntologyManagementPage = React.lazy(() => import('../pages/OntologyManagementPage'));
// const VerificationPage = React.lazy(() => import('../pages/VerificationPage'));
// const UserProfilePage = React.lazy(() => import('../pages/UserProfilePage'));
// const AdminDashboardPage = React.lazy(() => import('../pages/AdminDashboardPage'));
// const NotFoundPage = React.lazy(() => import('../pages/NotFoundPage'));

// Если не используете ленивую загрузку, импортируйте напрямую:
import OntologyManagementPageDirect from '../pages/OntologyManagementPage';
// import LoginPageDirect from '../pages/LoginPage'; // Пример


export function AppRouter() {
  return (
    // Suspense нужен, если используете React.lazy для страниц
    <Suspense fallback={<Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />}>
      <Routes>
        {/* Маршруты, использующие MainLayout (обычно для аутентифицированных пользователей) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Главная страница после логина, например, Исследователь Данных */}
          {/* <Route index element={<DataExplorerPage />} /> */}
          {/* <Route path="data-explorer" element={<DataExplorerPage />} /> */}
          
          {/* Наша страница управления онтологией */}
          <Route 
            path="ontology-management" 
            // element={<OntologyManagementPage />} // Для ленивой загрузки
            element={<OntologyManagementPageDirect />} // Для прямого импорта
          />
          {/* Для MVP adminOnly в ProtectedRoute можно не использовать, если страница просто доступна */}
          
          {/* Другие маршруты, требующие MainLayout и аутентификации */}
          {/* <Route path="profile" element={<UserProfilePage />} /> */}
          {/* <Route path="admin/verification" element={<VerificationPage />} /> */}
          {/* <Route path="admin/dashboard" element={<AdminDashboardPage />} /> */}

           {/* Заглушка для главной страницы, если DataExplorerPage еще нет */}
           <Route index element={<div>Добро пожаловать! (Главная страница)</div>} />
        </Route>

        {/* Маршруты, использующие AuthLayout (например, для логина) */}
        <Route element={<AuthLayout />}>
          {/* <Route path="/login" element={<LoginPageDirect />} /> */}
           <Route path="/login" element={<div>Страница Логина</div>} /> {/* Заглушка */}
        </Route>

        {/* Страница "Не найдено" (404) */}
        {/* <Route path="*" element={<NotFoundPage />} /> */}
        <Route path="*" element={<div>404 - Страница не найдена</div>} /> {/* Заглушка */}
      </Routes>
    </Suspense>
  );
}