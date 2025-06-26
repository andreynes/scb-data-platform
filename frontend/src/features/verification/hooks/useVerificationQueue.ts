// frontend/src/features/verification/hooks/useVerificationQueue.ts
import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
  fetchVerificationQueueThunk as fetchVerificationQueue,
  selectVerificationQueueTasks,
  selectVerificationQueueIsLoading,
  selectVerificationQueueError,
} from '../verificationSlice'; // Путь может отличаться

export const useVerificationQueue = () => {
  const dispatch = useAppDispatch();

  const tasks = useAppSelector(selectVerificationQueueTasks);
  const isLoading = useAppSelector(selectVerificationQueueIsLoading);
  const error = useAppSelector(selectVerificationQueueError);

  const fetchQueue = useCallback(
    (params?: { limit?: number; offset?: number }) => {
      // Диспатчим thunk для получения данных
      dispatch(fetchVerificationQueueThunk(params || {}));
    },
    [dispatch]
  );

  return {
    tasks,
    isLoading,
    error,
    fetchQueue,
  };
};