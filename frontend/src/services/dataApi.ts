// frontend/src/services/dataApi.ts

// 1. Импортируем РЕАЛЬНЫЙ сервис и все нужные схемы
import { 
  DataQueryService, 
  DataQuerySchema, 
  DataQueryResponseSchema 
} from './generated';

// Тип для формата экспорта, если он у вас есть в схемах, иначе его можно убрать
// import type { ExportFormat } from './generated';

/**
 * Выполняет запрос данных к СКЛАДА.
 * @param queryParams - Параметры запроса (фильтры, агрегации, и т.д.).
 * @returns Promise, который разрешается объектом DataQueryResponseSchema.
 * @throws Ошибку, если API возвращает ошибку.
 */
export const fetchDataQuery = async (queryParams: DataQuerySchema): Promise<DataQueryResponseSchema> => {
  try {
    // 2. Вызываем метод НАПРЯМУЮ у импортированного сервиса
    const response = await DataQueryService.queryDataApiV1DataQueryPost({
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
 * Инициирует асинхронный экспорт данных. (ЕСЛИ ОН ЕСТЬ)
 * Если эндпоинта /export еще нет, этот код можно закомментировать или удалить.
 */
/*
export const startDataExport = async (
  queryParams: DataQuerySchema,
  format: ExportFormat // Убедитесь, что тип ExportFormat существует в generated
): Promise<void> => {
  try {
    // Генератор, скорее всего, создаст метод с таким именем
    await DataQueryService.exportDataApiV1DataExportPost({
      requestBody: queryParams,
      format: format,
    });
  } catch (error) {
    console.error("Data export API error:", error);
    throw error;
  }
};
*/