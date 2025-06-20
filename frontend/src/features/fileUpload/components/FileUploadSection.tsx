// frontend/src/features/fileUpload/components/FileUploadSection.tsx

import React from 'react';
import { Button, Space } from 'antd'; // Добавил Space и Button для удобства

// ПРАВИЛЬНЫЙ ИМПОРТ: Мы изменили этот файл на именованный экспорт
import { FileUploadDropzone } from './FileUploadDropzone'; 

// ПРАВИЛЬНЫЙ ИМПОРТ: А этот файл, скорее всего, всё еще использует экспорт по умолчанию
import FileUploadList from './FileUploadList'; 

// ПРАВИЛЬНЫЙ ИМПОРТ: Хуки часто экспортируются как именованные
import { useFileUploadManager } from '../hooks/useFileUploadManager';

// Экспортируем этот компонент тоже как именованный для единообразия
export const FileUploadSection = () => {
    // Получаем все необходимые данные и функции из нашего хука-менеджера
    const { 
        uploads, 
        handleUploadStart, 
        clearCompleted,
        // Можно добавить и другие хендлеры, если хук их предоставляет
    } = useFileUploadManager();

    // Проверяем, есть ли завершенные (успешно или с ошибкой) загрузки
    const hasCompletedUploads = uploads.some(
        (up) => up.status === 'success' || up.status === 'error'
    );

    return (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* Компонент для выбора файлов */}
            <FileUploadDropzone 
                onUploadStart={handleUploadStart} 
                // можно передать и другие пропсы, например, disabled={isLoading}
            />

            {/* Компонент для отображения списка загружаемых файлов */}
            <FileUploadList uploads={uploads} />

            {/* Кнопка для очистки списка, появляется только когда есть что очищать */}
            {hasCompletedUploads && (
                <div style={{ textAlign: 'right', marginTop: '16px' }}>
                    <Button onClick={clearCompleted}>
                        Очистить завершенные
                    </Button>
                </div>
            )}
        </Space>
    );
};