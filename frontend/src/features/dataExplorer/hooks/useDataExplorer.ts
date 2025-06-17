// frontend/src/features/dataExplorer/hooks/useDataExplorer.ts

import { useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '../../../app/hooks';
import {
  // Селекторы для получения данных из Redux-состояния
  selectQueryParams,
  selectQueryResult,
  selectDataQueryStatus, // <--- ИСПРАВЛЕНИЕ 1: Импортируем правильный селектор статуса
  selectDataQueryError,
  selectExportStatus,
  selectExportError,
  // Thunks для асинхронных действий
  fetchDataQueryThunk,  // <--- ИСПРАВЛЕНИЕ 2: Правильное имя Thunk'а
  exportDataThunk,      // <--- ИСПРАВЛЕНИЕ 3: Правильное имя Thunk'а
  // Actions для синхронных действий
  setQueryParams as setQueryParamsAction,
} from '../slice';
import type { DataQuerySchema, ExportFormat, DataQueryResponseSchema } from '../../../services/generated';

// Определяем тип возвращаемого значения хука для удобства
export interface DataExplorerHookResult {
  queryParams: DataQuerySchema;
  setQueryParams: (params: Partial<DataQuerySchema>) => void;
  queryResult: DataQueryResponseSchema | null; // <--- Улучшенная типизация
  isLoading: boolean;
  error: string | null;
  executeQuery: () => Promise<any>;
  startExport: (format: ExportFormat) => Promise<any>;
  exportStatus: 'idle' | 'pending' | 'succeeded' | 'failed';
  exportError: string | null;
}

export function useDataExplorer(): DataExplorerHookResult {
  const dispatch = useAppDispatch();

  // Получаем все необходимые данные из Redux store с помощью селекторов
  const queryParams = useAppSelector(selectQueryParams);
  const queryResult = useAppSelector(selectQueryResult);
  const status = useAppSelector(selectDataQueryStatus); // <--- ИСПРАВЛЕНИЕ 4: Используем правильный селектор
  const isLoading = status === 'loading'; // Вычисляем isLoading на основе статуса
  const error = useAppSelector(selectDataQueryError);
  const exportStatus = useAppSelector(selectExportStatus);
  const exportError = useAppSelector(selectExportError);

  const setQueryParams = useCallback(
    (params: Partial<DataQuerySchema>) => {
      dispatch(setQueryParamsAction(params));
    },
    [dispatch]
  );

  const executeQuery = useCallback(async () => {
    // Диспатчим thunk для выполнения запроса данных
    // Передаем void (или ничего), так как thunk не ожидает аргументов
    return dispatch(fetchDataQueryThunk()).unwrap(); // <--- ИСПРАВЛЕНИЕ 5: Правильное имя и вызов
  }, [dispatch]);

  const startExport = useCallback(
    async (format: ExportFormat) => {
      // Диспатчим thunk для запуска экспорта
      return dispatch(exportDataThunk({ format })).unwrap(); // <--- ИСПРАВЛЕНИЕ 6: Правильное имя и передача объекта
    },
    [dispatch]
  );

  return {
    queryParams,
    setQueryParams,
    queryResult,
    isLoading,
    error,
    executeQuery,
    startExport,
    exportStatus,
    exportError,
  };
}