// frontend/src/app/store.ts
import { configureStore } from '@reduxjs/toolkit';

// --- Используем абсолютные пути, которые мы настроили ---
import authReducer from '~/features/auth/slice';
import ontologyManagementReducer from '~/features/ontologyManagement/slice';
import dataExplorerReducer from '~/features/dataExplorer/slice';
import verificationReducer from '../features/verification/verificationSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    ontologyManagement: ontologyManagementReducer,
    dataExplorer: dataExplorerReducer,
    verification: verificationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;