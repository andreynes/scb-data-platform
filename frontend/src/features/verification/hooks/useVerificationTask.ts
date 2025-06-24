// frontend/src/features/verification/hooks/useVerificationTask.ts
import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
  fetchVerificationTaskData as fetchTaskDataThunk,
  submitVerificationResult as submitResultThunk,
  selectCurrentVerificationTaskData,
  selectCurrentVerificationTaskStatus,
  selectCurrentVerificationTaskError,
  selectVerificationSubmitStatus,
  selectVerificationSubmitError,
  clearCurrentVerificationTask,
  // Actions для исправлений, которые понадобятся позже
  // addOrUpdateCorrectionAction,
  // clearCorrectionsAction,
} from '../verificationSlice';
import type { VerificationResultSchema, VerificationStatus } from '../../../services/generated';

export const useVerificationTask = (taskId: string | null) => {
  const dispatch = useAppDispatch();

  // Получаем состояние текущей задачи из Redux store
  const verificationData = useAppSelector(selectCurrentVerificationTaskData);
  const isLoading = useAppSelector(selectCurrentVerificationTaskStatus) === 'loading';
  const error = useAppSelector(selectCurrentVerificationTaskError);

  // Получаем состояние процесса отправки результата
  const isSubmitting = useAppSelector(selectVerificationSubmitStatus) === 'pending';
  const submitError = useAppSelector(selectVerificationSubmitError);

  // Загружаем данные, если taskId изменился и не равен null
  useEffect(() => {
    if (taskId) {
      dispatch(fetchTaskDataThunk(taskId));
    } else {
      // Очищаем данные, если задача была снята с выбора
      dispatch(clearCurrentVerificationTask());
    }
  }, [taskId, dispatch]);

  // Функция для отправки результата верификации
  const submitVerification = useCallback(
    async (status: VerificationStatus) => {
      if (!taskId || isSubmitting) {
        return Promise.reject("Task ID is missing or submission is already in progress.");
      }
      
      const result: VerificationResultSchema = {
        document_id: taskId,
        final_status: status,
        // На этом этапе исправления не отправляем
        // corrections: [],
      };

      return dispatch(submitResultThunk(result)).unwrap();
    },
    [dispatch, taskId, isSubmitting]
  );

  return {
    verificationData,
    isLoading,
    error,
    isSubmitting,
    submitError,
    submitVerification,
    // applyCorrection, // Добавим на этапе 5
    // cancelVerification, // Добавим на этапе 5
  };
};