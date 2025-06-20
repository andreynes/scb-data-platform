// frontend/src/features/auth/slice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as authApi from '../../services/authApi';
import type { RootState } from '../../app/store';
import type { UserSchema, TokenSchema, LoginFormData } from './types';

// Тип для состояния этого среза
interface AuthState {
  user: UserSchema | null;
  token: string | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

// Начальное состояние
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('authToken'), // Пытаемся взять токен из localStorage при запуске
  status: 'idle',
  error: null,
};

// Асинхронный Thunk для входа в систему
export const loginUser = createAsyncThunk<
  { token: string }, // Что возвращаем при успехе
  LoginFormData, // Что принимаем в качестве аргумента
  { rejectValue: string } // Тип для ошибки
>(
  'auth/loginUser',
  async (credentials, { dispatch, rejectWithValue }) => {
    try {
      const tokenData = await authApi.login(credentials);
      localStorage.setItem('authToken', tokenData.access_token);
      // После успешного логина, сразу запрашиваем данные пользователя
      dispatch(fetchUserMe()); 
      return { token: tokenData.access_token };
    } catch (error: any) {
      return rejectWithValue(error.detail || 'Failed to login');
    }
  }
);

// Асинхронный Thunk для получения данных текущего пользователя
export const fetchUserMe = createAsyncThunk<
  UserSchema, // Что возвращаем при успехе
  void, // Нет аргументов
  { rejectValue: string } // Тип для ошибки
>(
  'auth/fetchUserMe',
  async (_, { rejectWithValue }) => {
    try {
      const userData = await authApi.fetchCurrentUser();
      return userData;
    } catch (error: any) {
      localStorage.removeItem('authToken'); // Если токен невалиден, удаляем его
      return rejectWithValue(error.detail || 'Failed to fetch user');
    }
  }
);

// Создание среза
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Синхронный action для выхода
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.status = 'idle';
      state.error = null;
      localStorage.removeItem('authToken');
    },
  },
  // Обработка состояний асинхронных thunks
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Unknown login error';
      })
      .addCase(fetchUserMe.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchUserMe.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(fetchUserMe.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Unknown error fetching user';
        state.user = null;
        state.token = null;
      });
  },
});

export const { logout } = authSlice.actions;

// Селекторы для доступа к состоянию
export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState): boolean => !!state.auth.token;
export const selectAuthIsLoading = (state: RootState) => state.auth.status === 'loading';
export const selectAuthError = (state: RootState) => state.auth.error;

export default authSlice.reducer;