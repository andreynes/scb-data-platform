import React, { useEffect } from 'react'; // Убедитесь, что useEffect импортирован
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import { BrowserRouter } from 'react-router-dom';
import { store } from './app/store';
import { AppRouter } from './app/router';
import { useAppDispatch, useAppSelector } from './app/hooks'; // Предполагаем, что хуки вынесены
import { fetchUserMe, selectAuthToken, selectCurrentUser } from './features/auth/slice';

// Вспомогательный компонент, чтобы иметь доступ к Redux store
function AppContent() {
  const dispatch = useAppDispatch();
  const token = useAppSelector(selectAuthToken);
  const user = useAppSelector(selectCurrentUser);

  // --- КЛЮЧЕВОЕ ДОБАВЛЕНИЕ ---
  useEffect(() => {
    // Если есть токен, но нет данных пользователя, пытаемся их загрузить
    if (token && !user) {
      dispatch(fetchUserMe());
    }
  }, [token, user, dispatch]);
  // -------------------------

  return <AppRouter />;
}

function App() {
  return (
    <Provider store={store}>
      <ConfigProvider /* ...ваши настройки темы... */>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </ConfigProvider>
    </Provider>
  );
}

export default App;