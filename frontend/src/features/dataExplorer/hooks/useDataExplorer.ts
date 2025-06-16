// frontend/src/features/dataExplorer/hooks/useDataExplorer.ts

import { useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '../../../app/hooks';
import {
  // Селекторы для получения данных из Redux-состояния
  selectQueryParams,
  selectQueryResult,
  selectIsQueryLoading,
  selectQueryError,
  selectExportStatus,
  selectExportError,
  // Thunks для асинхронных действий
  fetchDataQuery,
  startDataExport,
  // Actions для синхронных действий
  setQueryParams as setQueryParamsAction,
} from '../slice';
import type { DataQuerySchema, ExportFormat } from '../../../services/generated';

// Определяем тип возвращаемого значения хука для удобства
export interface DataExplorerHookResult {
  queryParams: DataQuerySchema;
  setQueryParams: (params: Partial<DataQuerySchema>) => void;
  queryResult: any; // TODO: Заменить на DataQueryResponseSchema | null
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
  const isLoading = useAppSelector(selectIsQueryLoading);
  const error = useAppSelector(selectQueryError);
  const exportStatus = useAppSelector(selectExportStatus);
  const exportError = useAppSelector(selectExportError);

  // Создаем мемоизированные колбэки для действий, чтобы избежать лишних перерисовок
  const setQueryParams = useCallback(
    (params: Partial<DataQuerySchema>) => {
      dispatch(setQueryParamsAction(params));
    },
    [dispatch]
  );

  const executeQuery = useCallback(async () => {
    // Диспатчим thunk для выполнения запроса данных
    return dispatch(fetchDataQuery(queryParams)).unwrap();
  }, [dispatch, queryParams]);

  const startExport = useCallback(
    async (format: ExportFormat) => {
      // Диспатчим thunk для запуска экспорта
      return dispatch(startDataExport({ queryParams, format })).unwrap();
    },
    [dispatch, queryParams]
  );

  // Возвращаем состояние и функции для использования в компонентах
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