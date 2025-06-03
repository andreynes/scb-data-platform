// frontend/src/services/filesApi.ts
import { apiClient } from './apiClient'; // Предполагаем, что у вас есть настроенный apiClient
// ИЛИ, если вы используете напрямую сгенерированный клиент:
// import { FilesService, FileUploadStatusSchema } from './generated'; // Путь может отличаться
// import type { FileUploadStatusSchema } from './generated'; // Если типы отдельно

// Определим тип для ответа, если он еще не сгенерирован или не импортирован
// Этот тип должен соответствовать FileUploadStatusSchema из вашего бэкенда
export interface FileUploadStatus {
    filename: string;
    document_id: string;
    status: 'Accepted' | 'Processing' | 'Error' | 'Completed'; // Статусы из вашей схемы
    error_message?: string | null;
}

/**
 * Загружает один или несколько файлов на сервер.
 * @param files Массив объектов File для загрузки.
 * @param onUploadProgress (Опционально) Колбэк для отслеживания прогресса загрузки.
 * @returns Promise со списком статусов начальной обработки для каждого файла.
 * @throws Ошибку, если API вернул ошибку или произошла сетевая ошибка.
 */
export const uploadFiles = async (
    files: File[],
    // Колбэк для прогресса может быть сложнее реализовать без Axios или кастомного fetch
    // Для MVP можно пока опустить, если используется стандартный fetch из generated клиента
    // onUploadProgress?: (fileUid: string, percent: number) => void 
): Promise<FileUploadStatus[]> => {
    const formData = new FormData();
    files.forEach((file) => {
        // Ключ 'files' должен совпадать с тем, что ожидает FastAPI эндпоинт
        // в параметре files: List[UploadFile] = File(...)
        formData.append('files', file, file.name);
    });

    try {
        // Вариант 1: Используем кастомный apiClient (предпочтительнее, если он настроен с токенами и т.д.)
        // Убедитесь, что apiClient.post умеет работать с FormData и корректно устанавливает Content-Type
        // Возможно, Content-Type установится автоматически браузером для FormData
        const response = await apiClient.post<FileUploadStatus[]>('/api/v1/files/upload', formData, {
            headers: {
                // 'Content-Type': 'multipart/form-data' // Обычно устанавливается автоматически для FormData
            },
            // onUploadProgress: (progressEvent) => {
            //     if (onUploadProgress && progressEvent.total) {
            //         const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            //         // Здесь нужна логика для определения, к какому файлу относится этот progressEvent,
            //         // если загружается несколько файлов. Axios может предоставлять это для каждого файла.
            //         // Для простоты пока на весь батч или опускаем.
            //         // onUploadProgress('some_uid', percentCompleted); 
            //     }
            // }
        });
        return response.data;

        // Вариант 2: Если используете напрямую сгенерированный клиент (например, openapi-typescript-codegen)
        // Имя сервиса и метода будет зависеть от вашей OpenAPI спецификации и генератора
        // const response = await FilesService.uploadFilesApiV1FilesUploadPost({ 
        //     formData: { files: files } // Формат передачи formData зависит от генератора
        // });
        // return response; // Тип response должен быть FileUploadStatusSchema[] или совместимым

    } catch (error: any) {
        console.error("Ошибка при загрузке файлов:", error);
        // Пробрасываем ошибку для обработки в вызывающем коде (например, в хуке)
        // Можно извлечь более детальное сообщение из error.response.data.detail, если есть
        throw error.response?.data || error; 
    }
};

// Можно добавить другие функции для работы с файлами, если они понадобятся,
// например, для получения списка файлов, удаления и т.д.