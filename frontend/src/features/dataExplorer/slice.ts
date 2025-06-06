// frontend/src/features/dataExplorer/slice.ts
import * as RTK from '@reduxjs/toolkit'; 

const { createSlice, createAsyncThunk } = RTK;
// Для PayloadAction будем использовать RTK.PayloadAction в типизации

import * as dataApi from '../../services/dataApi'; // Импортируем наш сервисный файл для данных
import type {
    DataQuerySchema,
    DataQueryResponseSchema,
    // AtomicDataRow // Раскомментируйте, если нужен будет этот тип явно
} from '../../services/generated'; 
import type { RootState } from '../../app/store'; // Для типизации getState в Thunk, если понадобится

// Описываем состояние для фичи Исследователя Данных
interface DataExplorerState {
    currentQueryParams: DataQuerySchema | null; // Текущие параметры запроса (например, document_id)
    queryResult: DataQueryResponseSchema | null; // Результат последнего запроса
    isLoadingData: boolean; // Статус загрузки данных
    errorData: string | null; // Ошибка загрузки данных
}

const initialState: DataExplorerState = {
    currentQueryParams: null,
    queryResult: null,
    isLoadingData: false,
    errorData: null,
};

// Асинхронный Thunk для запроса данных из СКЛАДА
export const fetchDataQueryThunk = createAsyncThunk<
    DataQueryResponseSchema,    // Тип возвращаемых данных при успехе
    DataQuerySchema,            // Тип аргумента Thunk'а (наши queryParams)
    { rejectValue: string }      // Тип для ошибки (через rejectWithValue)
>(
    'dataExplorer/fetchData',     // Имя действия (featureName/thunkName)
    async (queryParams, { rejectWithValue }) => {
        try {
            // Вызываем сервисную функцию, созданную на предыдущем шаге
            const response = await dataApi.fetchDataForDocument(queryParams);
            return response;
        } catch (error: any) {
            const errorMessage = 
                error.response?.data?.detail || 
                error.message ||                
                'Failed to fetch data from warehouse';
            return rejectWithValue(errorMessage);
        }
    }
);

const dataExplorerSlice = createSlice({
    name: 'dataExplorer',
    initialState,
    reducers: {
        // Синхронный action для установки/изменения параметров запроса
        setQueryParams: (state, action: RTK.PayloadAction<DataQuerySchema>) => {
            state.currentQueryParams = action.payload;
            state.queryResult = null; 
            state.isLoadingData = false;
            state.errorData = null;
        },
        clearDataExplorerError: (state) => {
            state.errorData = null;
            if (state.isLoadingData && state.status === 'failed') { // Проверяем status, если он есть в вашем DataExplorerState
                 state.isLoadingData = false; // или status = 'idle'
            }
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDataQueryThunk.pending, (state) => {
                state.isLoadingData = true;
                state.errorData = null;
                state.queryResult = null;
            })
            .addCase(fetchDataQueryThunk.fulfilled, (state, action: RTK.PayloadAction<DataQueryResponseSchema>) => {
                state.isLoadingData = false;
                state.queryResult = action.payload;
            })
            .addCase(fetchDataQueryThunk.rejected, (state, action: RTK.PayloadAction<string | undefined>) => {
                state.isLoadingData = false;
                state.errorData = action.payload || 'An unknown error occurred while fetching data';
            });
    },
});

export const { 
    setQueryParams, 
    clearDataExplorerError 
} = dataExplorerSlice.actions;

// Селекторы
export const selectCurrentQueryParams = (state: RootState): DataQuerySchema | null => state.dataExplorer.currentQueryParams;
export const selectQueryResult = (state: RootState): DataQueryResponseSchema | null => state.dataExplorer.queryResult;
export const selectIsLoadingData = (state: RootState): boolean => state.dataExplorer.isLoadingData;
export const selectDataError = (state: RootState): string | null => state.dataExplorer.errorData;
// Добавляем селектор для всего состояния фичи, если это нужно
// export const selectDataExplorerState = (state: RootState): DataExplorerState => state.dataExplorer;

export default dataExplorerSlice.reducer;