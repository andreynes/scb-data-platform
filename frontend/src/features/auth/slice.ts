// frontend/src/features/auth/slice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as authApi from '../../services/authApi';
import type { RootState } from '../../app/store';
import type { UserSchema, TokenSchema, LoginFormData } from './types';

interface AuthState {
  user: UserSchema | null;
  token: string | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('authToken'),
  status: 'idle',
  error: null,
};

// --- ИЗМЕНЕНИЕ 1: fetchUserMe теперь может принимать токен как аргумент ---
export const fetchUserMe = createAsyncThunk<
  UserSchema,
  string | undefined, // Аргумент: опциональный токен
  { rejectValue: string }
>(
  'auth/fetchUserMe',
  async (token, { getState, rejectWithValue }) => {
    try {
      // Если токен не передан, пытаемся взять его из state
      const tokenToUse = token ?? (getState() as RootState).auth.token;
      
      if (!tokenToUse) {
        return rejectWithValue('No token found');
      }

      // Передаем токен напрямую в API-функцию
      const userData = await authApi.fetchCurrentUser(tokenToUse);
      return userData;
    } catch (error: any) {
      localStorage.removeItem('authToken');
      return rejectWithValue(error.detail || 'Failed to fetch user');
    }
  }
);


export const loginUser = createAsyncThunk<
  { token: string },
  LoginFormData,
  { rejectValue: string }
>(
  'auth/loginUser',
  async (credentials, { dispatch, rejectWithValue }) => {
    try {
      const tokenData = await authApi.login(credentials);
      const accessToken = tokenData.access_token;

      localStorage.setItem('authToken', accessToken);
      
      // --- ИЗМЕНЕНИЕ 2: Передаем свежий токен НАПРЯМУЮ в fetchUserMe ---
      // Это гарантирует, что запрос /me уйдет с правильным токеном
      await dispatch(fetchUserMe(accessToken)); 
      
      return { token: accessToken };
    } catch (error: any) {
      return rejectWithValue(error.detail || 'Failed to login');
    }
  }
);


const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.status = 'idle';
      state.error = null;
      localStorage.removeItem('authToken');
    },
  },
  extraReducers: (builder) => {
    builder
      // ... (все остальные extraReducers остаются без изменений)
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

export const selectCurrentUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState): boolean => !!state.auth.token;
export const selectAuthIsLoading = (state: RootState) => state.auth.status === 'loading';
export const selectAuthError = (state: RootState) => state.auth.error;

export default authSlice.reducer;