// frontend/src/app/store.ts
import * as RTK from '@reduxjs/toolkit';
const { configureStore } = RTK; 

// Импортируем редьюсеры из наших фич
// Предполагается, что authSlice.ts уже существует или будет создан позже
// import authReducer from '../features/auth/authSlice'; // Пример для аутентификации
import ontologyManagementReducer from '../features/ontologyManagement/ontologySlice';

export const store = configureStore({
  reducer: {
    // Здесь мы будем регистрировать все редьюсеры нашего приложения
    // auth: authReducer, // Пример
    ontologyManagement: ontologyManagementReducer,
    // Добавьте другие редьюсеры здесь, когда они появятся
    // например: dataExplorer: dataExplorerReducer,
  },
  // Middleware обычно настраивается автоматически Redux Toolkit,
  // но если вам нужны специфичные middleware (например, для RTK Query),
  // их можно добавить здесь:
  // middleware: (getDefaultMiddleware) =>
  //   getDefaultMiddleware().concat(myCustomMiddleware, loggerMiddleware),
});

// Типизация для использования с React-Redux
// Определяем тип RootState на основе состояния, которое хранит store
export type RootState = ReturnType<typeof store.getState>;

// Определяем тип AppDispatch для типизированного хука useDispatch
export type AppDispatch = typeof store.dispatch;

// Определяем тип AppThunk для асинхронных thunks, если они будут использоваться напрямую
// (хотя createAsyncThunk уже типизирован)
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;