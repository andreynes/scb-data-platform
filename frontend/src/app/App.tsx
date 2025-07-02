// frontend/src/app/App.tsx (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import React from 'react';
// Убираем импорт BrowserRouter, он нам здесь больше не нужен
import { AppRouter } from './router';

function App() {
  return (
    // Просто возвращаем AppRouter, без лишней обертки
    <AppRouter />
  );
}

export default App;