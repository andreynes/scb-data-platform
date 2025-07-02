import { apiClient } from './apiClient';
import type { 
  DataQuerySchema, 
  DataQueryResponseSchema,
  ExportFormat,
  ExportResponseSchema
} from './generated';

/**
 * Выполняет запрос данных к СКЛАДУ.
 */
export const fetchDataQuery = async (queryParams: DataQuerySchema): Promise<DataQueryResponseSchema> => {
  try {
    const response = await apiClient.post('/data/query', queryParams);
    return response.data;
  } catch (error) {
    console.error("Data query API error:", error);
    throw error;
  }
};

/**
 * Инициирует асинхронный экспорт данных.
 */
export const startDataExport = async (queryParams: DataQuerySchema, format: ExportFormat): Promise<ExportResponseSchema | void> => {
  try {
    const response = await apiClient.post(`/data/export?format=${format}`, queryParams);
    return response.data;
  } catch (error) {
    console.error("Data export API error:", error);
    throw error;
  }
};

// === НОВАЯ ФУНКЦИЯ ДЛЯ "ТРЕВОЖНОЙ КНОПКИ" ===
/**
 * Помечает документ как требующий верификации.
 * @param documentId ID документа для пометки.
 */
export const flagDocumentForVerification = async (documentId: string): Promise<void> => {
  if (!documentId) {
    console.error("flagDocumentForVerification: documentId is required.");
    // Можно выбросить ошибку или просто ничего не делать
    return Promise.reject(new Error("Document ID is required."));
  }
  
  try {
    // В ТЗ 3.5.4 указано, что "Тревожная кнопка" инициирует проверку.
    // Эндпоинт для этого, согласно нашему плану, должен быть на бэкенде.
    // POST /data/{document_id}/flag-for-verification
    // Предположим такой URL для API:
    await apiClient.post(`/data/${documentId}/flag-for-verification`);
  } catch (error) {
    console.error(`Error flagging document ${documentId} for verification:`, error);
    throw error;
  }
};