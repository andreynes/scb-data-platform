// frontend/src/features/ontologyManagement/slice.ts
import * as RTK from '@reduxjs/toolkit'; // Импортируем всё под псевдонимом RTK

// Используем нужные части из RTK
const { createSlice, createAsyncThunk } = RTK;
// Для PayloadAction будем использовать RTK.PayloadAction в типизации

import { fetchOntologySchema as apiFetchOntologySchema } from '../../services/ontologyApi';
import type { OntologySchema } from '../../services/generated';
import type { RootState } from '../../app/store';

interface OntologyState {
  schema: OntologySchema | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: OntologyState = {
  schema: null,
  status: 'idle',
  error: null,
};

export const fetchActiveOntologySchema = createAsyncThunk<
  OntologySchema,
  void,
  { rejectValue: string }
>(
  'ontologyManagement/fetchSchema',
  async (_, { rejectWithValue }) => {
    try {
      const schemaData = await apiFetchOntologySchema();
      return schemaData;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch ontology schema';
      return rejectWithValue(errorMessage);
    }
  }
);

const ontologySlice = createSlice({
  name: 'ontologyManagement',
  initialState,
  reducers: {
    clearOntologyError: (state) => {
      state.error = null;
      if (state.status === 'failed') {
        state.status = 'idle';
      }
    },
    resetOntologyState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchActiveOntologySchema.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      // ИЗМЕНЕНИЕ ЗДЕСЬ: используем RTK.PayloadAction
      .addCase(fetchActiveOntologySchema.fulfilled, (state, action: RTK.PayloadAction<OntologySchema>) => {
        state.status = 'succeeded';
        state.schema = action.payload;
      })
      // И ИЗМЕНЕНИЕ ЗДЕСЬ: используем RTK.PayloadAction
      .addCase(fetchActiveOntologySchema.rejected, (state, action: RTK.PayloadAction<string | undefined>) => {
        state.status = 'failed';
        state.error = action.payload || 'An unknown error occurred';
        state.schema = null;
      });
  },
});

export const { clearOntologyError, resetOntologyState } = ontologySlice.actions;

export const selectOntologySchema = (state: RootState): OntologySchema | null => state.ontologyManagement.schema;
export const selectOntologyStatus = (state: RootState): OntologyState['status'] => state.ontologyManagement.status;
export const selectOntologyIsLoading = (state: RootState): boolean => state.ontologyManagement.status === 'loading';
export const selectOntologyError = (state: RootState): string | null => state.ontologyManagement.error;

export default ontologySlice.reducer;