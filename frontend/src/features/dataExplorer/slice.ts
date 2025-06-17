// frontend/src/features/dataExplorer/slice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// ИСПРАВЛЕНИЕ 1: Импортируем fetchDataQuery, а не fetchDataForDocument
import * as dataApi from '../../services/dataApi'; 
import type {
  DataQuerySchema,
  DataQueryResponseSchema,
  ExportFormat,
  // ExportResponseSchema, // Закомментировано, так как startDataExport возвращает void
  AtomicDataRow,
} from '../../services/generated';
import type { RootState } from '../../app/store';

interface DataExplorerState {
  queryParams: DataQuerySchema;
  queryResult: DataQueryResponseSchema | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
  exportStatus: 'idle' | 'pending' | 'succeeded' | 'failed';
  exportError: string | null;
}

const initialState: DataExplorerState = {
  queryParams: { document_id: '' },
  queryResult: null,
  status: 'idle',
  error: null,
  exportStatus: 'idle',
  exportError: null,
};

export const fetchDataQueryThunk = createAsyncThunk<
  DataQueryResponseSchema,
  void,
  { state: RootState; rejectValue: string }
>(
  'dataExplorer/fetchData',
  async (_, { getState, rejectWithValue }) => {
    try {
      const queryParams = getState().dataExplorer.queryParams;
      // ИСПРАВЛЕНИЕ 2: Вызываем правильную функцию из dataApi
      const response = await dataApi.fetchDataQuery(queryParams); 
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || error.message || 'Failed to fetch data'
      );
    }
  }
);

export const exportDataThunk = createAsyncThunk<
  void, // Возвращаемый тип void
  { format: ExportFormat },
  { state: RootState; rejectValue: string }
>(
  'dataExplorer/exportData',
  async ({ format }, { getState, rejectWithValue }) => {
    try {
      const queryParams = getState().dataExplorer.queryParams;
      await dataApi.startDataExport(queryParams, format);
      // Ничего не возвращаем, так как startDataExport возвращает void
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || error.message || 'Failed to start export'
      );
    }
  }
);

// ... остальной код слайса остается без изменений ...
// (createSlice, reducers, extraReducers, selectors)
const dataExplorerSlice = createSlice({
    name: 'dataExplorer',
    initialState,
    reducers: {
      setQueryParams: (state, action: PayloadAction<Partial<DataQuerySchema>>) => {
        state.queryParams = { ...state.queryParams, ...action.payload };
      },
      clearDataExplorerState: () => initialState,
    },
    extraReducers: (builder) => {
      builder
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
  
  export const selectQueryParams = (state: RootState) => state.dataExplorer.queryParams;
  export const selectQueryResult = (state: RootState) => state.dataExplorer.queryResult;
  export const selectDataQueryStatus = (state: RootState) => state.dataExplorer.status;
  export const selectDataQueryError = (state: RootState) => state.dataExplorer.error;
  export const selectExportStatus = (state: RootState) => state.dataExplorer.exportStatus;
  export const selectExportError = (state: RootState) => state.dataExplorer.exportError;
  
  export default dataExplorerSlice.reducer;