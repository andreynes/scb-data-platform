import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DataExplorerPage from '../pages/DataExplorerPage';

// Заглушка для страницы логина
const LoginPage = () => <h2>Страница Входа</h2>;

export function AppRouter() {
  return (
    <Routes>
      {/* Редирект с главной на исследователь данных */}
      <Route path="/" element={<Navigate to="/data-explorer" replace />} />
      <Route path="/data-explorer" element={<DataExplorerPage />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>
  );
}