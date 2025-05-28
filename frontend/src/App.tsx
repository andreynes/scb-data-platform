// frontend/src/App.tsx (или frontend/src/app/App.tsx)
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './app/store'; // Предполагая, что store.ts в app/
import { AppRouter } from './app/router'; // <-- ИМПОРТ AppRouter
import { ConfigProvider, App as AntApp } from 'antd'; // AntApp для message, notification
// import ruRU from 'antd/locale/ru_RU'; // Если нужна локализация AntD
// import { antThemeConfig } from './styles/theme'; // Если есть тема

function App() {
  return (
    <React.StrictMode>
      <Provider store={store}>
        {/* <ConfigProvider locale={ruRU} theme={antThemeConfig}> */}
        <ConfigProvider> {/* Упрощенный ConfigProvider */}
          <AntApp> {/* Обертка для message, notification, Modal.confirm из AntD */}
            <BrowserRouter>
              <AppRouter /> {/* <-- ИСПОЛЬЗОВАНИЕ AppRouter */}
            </BrowserRouter>
          </AntApp>
        </ConfigProvider>
      </Provider>
    </React.StrictMode>
  );
}

export default App;