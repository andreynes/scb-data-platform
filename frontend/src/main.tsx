// frontend/src/main.tsx (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

import React from 'react';
import ReactDOM from 'react-dom/client';

// 1. Для Redux
import { Provider } from 'react-redux';
import { store } from './app/store';

// 2. Для Роутинга
import { BrowserRouter } from 'react-router-dom';



// 4. Главный компонент приложения
import App from './app/App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Failed to find the root element with id 'root'");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    {/* Оборачиваем все приложение в Provider для Redux */}
    <Provider store={store}>
      {/* Оборачиваем все приложение в BrowserRouter для роутинга */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);