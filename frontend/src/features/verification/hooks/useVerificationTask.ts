// frontend/src/features/verification/hooks/useVerificationTask.ts
import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
  // Импортируем thunks под их реальными именами
  fetchVerificationTaskDataThunk, 
  submitVerificationResultThunk,
  
  // Импортируем селекторы под их реальными именами
  selectCurrentVerificationTaskData,
  selectCurrentVerificationTaskStatus,
  selectCurrentVerificationTaskError,
  selectVerificationSubmitStatus,
  selectVerificationSubmitError,

  // Импортируем обычные экшены
  clearCurrentVerificationTask,
} from '../verificationSlice';

import type { VerificationResultSchema, VerificationStatus } from '../../../services/generated';

export const useVerificationTask = (taskId: string | null) => {
  const dispatch = useAppDispatch();

  // Используем правильные имена селекторов
  const verificationData = useAppSelector(selectCurrentVerificationTaskData);
  const isLoading = useAppSelector(selectCurrentVerificationTaskStatus) === 'loading'; 
  const error = useAppSelector(selectCurrentVerificationTaskError);

  const isSubmitting = useAppSelector(selectVerificationSubmitStatus) === 'pending';
  const submitError = useAppSelector(selectVerificationSubmitError);

  useEffect(() => {
    if (taskId) {
      dispatch(fetchVerificationTaskDataThunk(taskId));
    } else {
      dispatch(clearCurrentVerificationTask());
    }
  }, [taskId, dispatch]);

  const submitVerification = useCallback(
    async (status: VerificationStatus) => {
      if (!taskId || isSubmitting) {
        return Promise.reject("Task ID is missing or submission is already in progress.");
      }
      
      const result: VerificationResultSchema = {
        document_id: taskId,
        final_status: status,
      };
      
      return dispatch(submitVerificationResultThunk(result)).unwrap();
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
  };
};