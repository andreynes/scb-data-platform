// frontend/src/services/dataApi.ts

// ИСПРАВЛЕНО: Используем правильное имя сервиса 'DataService'
import { 
  DataService, // <--- ВОТ ГЛАВНОЕ ИСПРАВЛЕНИЕ
  type DataQuerySchema, 
  type DataQueryResponseSchema,
  type ExportFormat 
} from './generated';

/**
 * Выполняет запрос данных к СКЛАДА.
 */
export const fetchDataQuery = async (queryParams: DataQuerySchema): Promise<DataQueryResponseSchema> => {
  try {
    // Вызываем метод у правильного сервиса DataService
    const response = await DataService.queryDataApiV1DataQueryPost({
      requestBody: queryParams,
    });
    return response;
  } catch (error) {
    console.error("Data query API error:", error);
    throw error; 
  }
};

/**
 * Инициирует асинхронный экспорт данных и возвращает Blob.
 */
export const startDataExport = async (
  queryParams: DataQuerySchema,
  format: ExportFormat
): Promise<Blob | null> => {
  try {
    // Вызываем метод у правильного сервиса DataService
    const response = await DataService.exportDataApiV1DataExportPost({
      requestBody: queryParams,
      format: format,
    });
    if (response instanceof Blob) {
      return response;
    }
    return null;
  } catch (error)
  {
    console.error("Data export API error:", error);
    throw error;
  }
};

/**
 * Помечает документ для ручной верификации ("тревожная кнопка").
 */
export const flagDocumentForVerification = async (
  documentId: string
): Promise<any> => {
  try {
    // Вызываем метод у правильного сервиса DataService
    const response = await DataService.flagForVerificationApiV1DataDocumentIdFlagForVerificationPost({
      documentId,
    });
    return response;
  } catch (error) {
    console.error(`Failed to flag document ${documentId} for verification:`, error);
    throw error;
  }
};