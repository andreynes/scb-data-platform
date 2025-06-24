// frontend/src/services/dataApi.ts

// 1. Импортируем РЕАЛЬНЫЙ сервис и все нужные схемы
import { 
  DataService, 
  DataQuerySchema, 
  DataQueryResponseSchema,
  ExportFormat, // Предполагаем, что этот Enum тоже сгенерирован
  ExportResponseSchema
} from './generated';

/**
 * Выполняет запрос данных к СКЛАДА.
 * @param queryParams - Параметры запроса (фильтры, агрегации, и т.д.).
 * @returns Promise, который разрешается объектом DataQueryResponseSchema.
 * @throws Ошибку, если API возвращает ошибку.
 */
export const fetchDataQuery = async (queryParams: DataQuerySchema): Promise<DataQueryResponseSchema> => {
  try {
    // 2. Вызываем метод НАПРЯМУЮ у импортированного сервиса
    const response = await DataService.queryDataApiV1DataQueryPost({
      requestBody: queryParams,
    });
    return response;
  } catch (error) {
    console.error("Data query API error:", error);
    // Пробрасываем ошибку для обработки выше (например, в UI или Redux)
    throw error; 
  }
};

/**
 * Инициирует асинхронный экспорт данных.
 */
export const startDataExport = async (
  queryParams: DataQuerySchema,
  format: ExportFormat
): Promise<ExportResponseSchema | void> => {
  try {
    const response = await DataService.exportDataApiV1DataExportPost({
      requestBody: queryParams,
      format: format,
    });
    return response;
  } catch (error) {
    console.error("Data export API error:", error);
    throw error;
  }
};

// <<< НАЧАЛО НОВОЙ ФУНКЦИИ >>>
/**
 * Помечает документ для ручной верификации ("тревожная кнопка").
 * @param documentId - ID документа для пометки.
 */
export const flagDocumentForVerification = async (
  documentId: string
): Promise<any> => {
  try {
    // Имя сгенерированной функции может отличаться в зависимости от operationId
    const response = await DataService.flagForVerificationApiV1DataDocumentIdFlagForVerificationPost({
      documentId,
    });
    return response;
  } catch (error) {
    console.error(`Failed to flag document ${documentId} for verification:`, error);
    throw error;
  }
};
// <<< КОНЕЦ НОВОЙ ФУНКЦИИ >>>