// frontend/src/features/ontologyManagement/ontologySlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { fetchOntologySchema as apiFetchOntologySchema } from '../../services/ontologyApi';
// Предполагаем, что типы схемы онтологии экспортируются из сгенерированного клиента
// или определены в отдельном файле типов, если сгенерированные слишком сложны для прямого использования
import type { OntologySchema } from '../../services/generated'; // Путь может отличаться
import type { RootState } from '../../app/store'; // Для типизации селекторов

interface OntologyState {
  schema: OntologySchema | null;
  // Возможно, в будущем здесь будут и vocabularies, status для них и т.д.
  // vocabularies: Record<string, any[]> | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: OntologyState = {
  schema: null,
  // vocabularies: null,
  status: 'idle', // 'idle' означает, что данные еще не загружались или загрузка сброшена
  error: null,
};

// Асинхронный Thunk для загрузки схемы онтологии
export const fetchActiveOntologySchema = createAsyncThunk<
  OntologySchema, // Тип возвращаемого значения при успехе
  void,           // Тип аргумента thunk'а (void, если аргументов нет)
  { rejectValue: string } // Тип значения для rejectWithValue при ошибке
>(
  'ontologyManagement/fetchSchema', // Префикс для action types (e.g., 'ontologyManagement/fetchSchema/pending')
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
  name: 'ontologyManagement', // Имя среза, будет использоваться как префикс в action types
  initialState,
  reducers: {
    // Здесь можно добавить синхронные reducers, если понадобятся
    // Например, для сброса ошибки или статуса
    clearOntologyError: (state) => {
      state.error = null;
      if (state.status === 'failed') { // Сбрасываем статус, если была ошибка, чтобы можно было попробовать снова
        state.status = 'idle';
      }
    },
    resetOntologyState: () => initialState, // Полный сброс состояния
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchActiveOntologySchema.pending, (state) => {
        state.status = 'loading';
        state.error = null; // Сбрасываем предыдущую ошибку при новой попытке
      })
      .addCase(fetchActiveOntologySchema.fulfilled, (state, action: PayloadAction<OntologySchema>) => {
        state.status = 'succeeded';
        state.schema = action.payload;
      })
      .addCase(fetchActiveOntologySchema.rejected, (state, action: PayloadAction<string | undefined>) => {
        state.status = 'failed';
        state.error = action.payload || 'An unknown error occurred';
        state.schema = null; // Очищаем схему при ошибке
      });
  },
});

// Экспортируем actions
export const { clearOntologyError, resetOntologyState } = ontologySlice.actions;

// Экспортируем селекторы для доступа к состоянию
export const selectOntologySchema = (state: RootState): OntologySchema | null => state.ontologyManagement.schema;
export const selectOntologyStatus = (state: RootState): OntologyState['status'] => state.ontologyManagement.status;
export const selectOntologyIsLoading = (state: RootState): boolean => state.ontologyManagement.status === 'loading';
export const selectOntologyError = (state: RootState): string | null => state.ontologyManagement.error;

// Экспортируем reducer
export default ontologySlice.reducer;