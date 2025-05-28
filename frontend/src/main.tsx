// frontend/src/main.tsx (или index.tsx)
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux'; // <-- ИМПОРТИРОВАТЬ Provider
import { store } from './app/store';    // <-- ИМПОРТИРОВАТЬ store
import App from './App'; // Или './app/App' в зависимости от вашей структуры
import './index.css'; // Или ваши глобальные стили

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error("Failed to find the root element with id 'root'");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <Provider store={store}> {/* <-- ОБЕРНУТЬ App В Provider */}
      <App />
    </Provider>
  </React.StrictMode>
);