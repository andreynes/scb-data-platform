import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app/App'; // Убедимся, что импортируем App

// Уберем пока все импорты стилей, чтобы исключить их влияние
// import './index.css'; 

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Failed to find the root element with id 'root'");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);