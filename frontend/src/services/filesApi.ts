// frontend/src/services/filesApi.ts
import apiClient from './apiClient'; // <-- ИСПРАВЛЕННЫЙ ИМПОРТ (без фигурных скобок)
import type { FileUploadStatusSchema } from './generated';

// Этот интерфейс нужен для хука useFileUploadManager
export interface UploadProgressInfo {
  uid: string;
  name: string;
  status: 'waiting' | 'uploading' | 'success' | 'error';
  percent?: number;
  response?: FileUploadStatusSchema;
  errorMessage?: string;
}

/**
 * Загружает файлы на сервер.
 * @param files - Массив файлов для загрузки.
 * @returns Promise с результатами загрузки.
 */
export const uploadFiles = async (files: File[]): Promise<FileUploadStatusSchema[]> => {
  const formData = new FormData();
  files.forEach(file => {
    // Ключ 'files' должен совпадать с тем, что ожидает FastAPI эндпоинт
    formData.append('files', file);
  });

  try {
    const response = await apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    // Пробрасываем ошибку, чтобы ее мог поймать хук useFileUploadManager
    console.error("File upload API error:", error);
    throw error.response?.data || error;
  }
};