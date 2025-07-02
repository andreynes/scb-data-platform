// Файл: frontend/src/features/auth/slice.ts (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as authApi from '../../services/authApi';
// ===== ИМПОРТИРУЕМ OpenAPI для управления токеном =====
import { OpenAPI } from '../../services/generated/core/OpenAPI';
import type { LoginCredentials } from '../../services/generated';
import type { UserSchema, TokenSchema } from '../../schemas/user_schemas';

interface AuthState {
    user: UserSchema | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
}

// Устанавливаем токен при первоначальной загрузке, если он есть в localStorage
const initialToken = localStorage.getItem('authToken');
if (initialToken) {
  OpenAPI.TOKEN = initialToken;
}

const initialState: AuthState = {
    user: null,
    status: 'idle',
    error: null,
};

export const loginUser = createAsyncThunk<UserSchema, LoginCredentials, { rejectValue: string }>(
  'auth/loginUser',
  async (credentials, { rejectWithValue }) => {
    try {
      // 1. Получаем токен
      const tokenData = await authApi.login(credentials);
      // 2. Устанавливаем его для будущих запросов
      OpenAPI.TOKEN = tokenData.access_token;
      localStorage.setItem('authToken', tokenData.access_token);
      // 3. Сразу запрашиваем пользователя
      const userData = await authApi.fetchCurrentUser();
      // 4. Возвращаем пользователя
      return userData;
    } catch (error: any) {
      // Чистим все в случае ошибки
      OpenAPI.TOKEN = undefined;
      localStorage.removeItem('authToken');
      return rejectWithValue(error?.response?.data?.detail || 'Неверное имя пользователя или пароль');
    }
  }
);

// Этот thunk нам больше не нужен, так как мы получаем юзера сразу после логина.
// Но оставим его для загрузки при обновлении страницы.
export const fetchInitialUser = createAsyncThunk<UserSchema, void, { rejectValue: string }>(
  'auth/fetchInitialUser',
  async (_, { rejectWithValue }) => {
    if (!OpenAPI.TOKEN) {
      return rejectWithValue('No token found');
    }
    try {
      return await authApi.fetchCurrentUser();
    } catch (error: any) {
      OpenAPI.TOKEN = undefined;
      localStorage.removeItem('authToken');
      return rejectWithValue('Could not fetch user');
    }
  }
);


const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logoutAction: (state) => {
      state.user = null;
      state.status = 'idle';
      OpenAPI.TOKEN = undefined;
      localStorage.removeItem('authToken');
    },
  },
  extraReducers: (builder) => {
    builder
      // loginUser
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      // fetchInitialUser
      .addCase(fetchInitialUser.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchInitialUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(fetchInitialUser.rejected, (state) => {
        state.status = 'idle'; // Просто сбрасываем, ошибки не показываем
      });
  },
});

export const { logoutAction } = authSlice.actions;

export const selectCurrentUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }): boolean => !!state.auth.user;
export const selectAuthIsLoading = (state: { auth: AuthState }) => state.auth.status === 'loading';
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;

export default authSlice.reducer;