import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

import * as dataApi from '../../services/dataApi';
import type {
  DataQuerySchema,
  DataQueryResponseSchema,
  ExportFormat,
  ExportResponseSchema,
} from '../../services/generated';
import type { RootState } from '../../app/store';

// Описываем состояние для фичи Исследователя Данных
interface DataExplorerState {
  queryParams: DataQuerySchema; // Параметры всегда существуют
  queryResult: DataQueryResponseSchema | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed'; // Единый статус для запроса данных
  error: string | null;

  exportStatus: 'idle' | 'pending' | 'succeeded' | 'failed';
  exportError: string | null;
}

const initialState: DataExplorerState = {
  // Для MVP можно начать с пустого document_id
  queryParams: { document_id: '' }, 
  queryResult: null,
  status: 'idle',
  error: null,
  exportStatus: 'idle',
  exportError: null,
};

// Асинхронный Thunk для запроса данных из СКЛАДА
export const fetchDataQueryThunk = createAsyncThunk<
  DataQueryResponseSchema,
  void, // Не принимает аргументов, берет их из state
  { state: RootState; rejectValue: string }
>(
  'dataExplorer/fetchData',
  async (_, { getState, rejectWithValue }) => {
    try {
      const queryParams = getState().dataExplorer.queryParams;
      const response = await dataApi.fetchDataForDocument(queryParams);
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || error.message || 'Failed to fetch data'
      );
    }
  }
);

// Асинхронный Thunk для экспорта данных
export const exportDataThunk = createAsyncThunk<
  ExportResponseSchema | void,
  { format: ExportFormat },
  { state: RootState; rejectValue: string }
>(
  'dataExplorer/exportData',
  async ({ format }, { getState, rejectWithValue }) => {
    try {
      const queryParams = getState().dataExplorer.queryParams;
      const response = await dataApi.startDataExport(queryParams, format);
      return response;
    } catch (error: any)      return rejectWithValue(
        error.response?.data?.detail || error.message || 'Failed to start export'
      );
    }
  }
);


const dataExplorerSlice = createSlice({
  name: 'dataExplorer',
  initialState,
  reducers: {
    setQueryParams: (state, action: PayloadAction<Partial<DataQuerySchema>>) => {
      // Обновляем только часть параметров, не сбрасывая все
      state.queryParams = { ...state.queryParams, ...action.payload };
    },
    clearDataExplorerState: () => initialState, // Action для полного сброса
  },
  extraReducers: (builder) => {
    builder
      // Обработчики для fetchDataQueryThunk
      .addCase(fetchDataQueryThunk.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchDataQueryThunk.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.queryResult = action.payload;
      })
      .addCase(fetchDataQueryThunk.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Unknown error';
      })
      // Обработчики для exportDataThunk
      .addCase(exportDataThunk.pending, (state) => {
        state.exportStatus = 'pending';
        state.exportError = null;
      })
      .addCase(exportDataThunk.fulfilled, (state) => {
        state.exportStatus = 'succeeded';
      })
      .addCase(exportDataThunk.rejected, (state, action) => {
        state.exportStatus = 'failed';
        state.exportError = action.payload ?? 'Unknown error';
      });
  },
});

export const { 
    setQueryParams, 
    clearDataExplorerState 
} = dataExplorerSlice.actions;

// Селекторы
export const selectQueryParams = (state: RootState) => state.dataExplorer.queryParams;
export const selectQueryResult = (state: RootState) => state.dataExplorer.queryResult;
export const selectDataQueryStatus = (state: RootState) => state.dataExplorer.status;
export const selectDataQueryError = (state: RootState) => state.dataExplorer.error;
export const selectExportStatus = (state: RootState) => state.dataExplorer.exportStatus;
export const selectExportError = (state: RootState) => state.dataExplorer.exportError;

export default dataExplorerSlice.reducer;