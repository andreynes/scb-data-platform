// frontend/src/main.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';

// 1. Импортируем Provider из react-redux
import { Provider } from 'react-redux';
// 2. Импортируем наш Redux store
import { store } from './app/store';

import App from './app/App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Failed to find the root element with id 'root'");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    {/* 3. Оборачиваем все приложение в Provider и передаем ему store */}
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);