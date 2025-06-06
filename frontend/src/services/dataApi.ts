// frontend/src/services/dataApi.ts
import {
    DataService, // Пример имени сгенерированного сервиса
    DataQuerySchema, // Схема запроса (содержит document_id)
    DataQueryResponseSchema // Схема ответа (содержит List[AtomicDataRow] и pagination)
} from './generated'; // Предполагается, что это путь к вашим сгенерированным типам/сервисам

/**
 * Запрашивает атомарные данные из СКЛАДА по ID документа.
 * @param queryParams - Параметры запроса, содержащие document_id.
 * @returns Promise с данными ответа или выбрасывает ошибку.
 */
export const fetchDataForDocument = async (
    queryParams: DataQuerySchema
): Promise<DataQueryResponseSchema> => {
    try {
        // Имя функции DataService.queryDataApiV1DataQueryPost может отличаться
        // в зависимости от вашего operationId в OpenAPI спецификации.
        // Проверьте сгенерированный код в services/generated/services/DataService.ts
        const response = await DataService.queryDataApiV1DataQueryPost({
            requestBody: queryParams // Сгенерированный клиент часто ожидает requestBody
        });
        return response;
    } catch (error) {
        console.error("Error fetching data for document:", error);
        // Пробрасываем ошибку дальше, чтобы ее мог обработать Redux Thunk или хук
        throw error;
    }
};

// TODO: В будущем здесь может быть функция для экспорта данных
// export const startDataExport = async (...): Promise<...> => { ... };