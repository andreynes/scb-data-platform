// frontend/src/services/dataApi.ts

// --- > ИЗМЕНЕНИЕ ЗДЕСЬ: Вместо 'DataService' импортируем 'DefaultService' и переименовываем < ---
import { DefaultService as DataService, DataQuerySchema, DataQueryResponseSchema, ExportFormat } from './generated';

/**
 * Выполняет запрос данных к СКЛАДА.
 * @param queryParams - Параметры запроса (фильтры, агрегации, и т.д.).
 * @returns Promise, который разрешается объектом DataQueryResponseSchema.
 * @throws Ошибку, если API возвращает ошибку.
 */
export const fetchDataQuery = async (queryParams: DataQuerySchema): Promise<DataQueryResponseSchema> => {
  try {
    // Вызов сгенерированной функции. Имя может отличаться, но обычно включает operationId.
    const response = await DataService.queryDataApiV1DataQueryPost({
      requestBody: queryParams,
    });
    return response;
  } catch (error) {
    console.error("Data query API error:", error);
    throw error; // Пробрасываем ошибку для обработки в Redux Thunk
  }
};

/**
 * Инициирует асинхронный экспорт данных.
 * @param queryParams - Параметры запроса для экспорта.
 * @param format - Желаемый формат экспорта ('excel' или 'csv').
 * @returns Promise, который может разрешаться объектом ExportResponseSchema или void.
 */
export const startDataExport = async (
  queryParams: DataQuerySchema,
  format: ExportFormat
): Promise<void> => { // Для MVP возвращаем void, так как статус 202 не имеет тела
  try {
    await DataService.exportDataApiV1DataExportPost({
      requestBody: queryParams,
      format: format,
    });
  } catch (error) {
    console.error("Data export API error:", error);
    throw error;
  }
};