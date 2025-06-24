// frontend/src/services/adminApi.ts
import {
  AdminService, // Имя сгенерированного сервиса может отличаться
  VerificationTaskSchema,
  VerificationDataSchema,
  VerificationResultSchema,
} from './generated';

/**
 * Запрашивает очередь задач на верификацию.
 */
export const fetchVerificationQueue = async (
  limit: number = 50,
  offset: number = 0
): Promise<VerificationTaskSchema[]> => {
  // Имя метода может отличаться в зависимости от operationId в OpenAPI
  return AdminService.getVerificationQueueAdminVerificationQueueGet({ limit, offset });
};

/**
 * Запрашивает данные для конкретной задачи верификации.
 */
export const fetchVerificationTaskData = async (
  taskId: string
): Promise<VerificationDataSchema> => {
  return AdminService.getVerificationTaskDataAdminVerificationTaskIdDataGet({ taskId });
};

/**
 * Отправляет результат ручной верификации.
 */
export const submitVerificationResult = async (
  result: VerificationResultSchema
): Promise<void> => {
  // API возвращает 204 No Content, поэтому результат Promise - void
  return AdminService.submitVerificationResultAdminVerificationSubmitPost({
    requestBody: result,
  });
};