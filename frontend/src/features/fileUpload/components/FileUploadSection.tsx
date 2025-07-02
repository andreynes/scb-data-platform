// Файл: frontend/src/features/fileUpload/components/FileUploadSection.tsx

import React from 'react';
import FileUploadDropzone from './FileUploadDropzone';
// === ИЗМЕНЕНО: Используем именованный импорт, если экспорт не дефолтный ===
import { FileUploadList } from './FileUploadList'; 
import { useFileUploadManager } from '../hooks/useFileUploadManager';

interface FileUploadSectionProps {
    onUploadSuccess: (docId: string, filename: string) => void;
}

export const FileUploadSection: React.FC<FileUploadSectionProps> = ({ onUploadSuccess }) => {
    const {
        uploads,
        handleUploadStart,
        clearCompleted,
    } = useFileUploadManager({ onUploadSuccess }); // Передаем колбэк в хук

    return (
        <div>
            <FileUploadDropzone
                onUploadStart={handleUploadStart}
                // Передаем другие необходимые пропсы, если они есть
            />
            <FileUploadList uploads={uploads} />
            {uploads.some(u => u.status === 'success' || u.status === 'error') && (
                 <Button onClick={clearCompleted} style={{ marginTop: 16 }}>
                    Очистить завершенные
                 </Button>
            )}
        </div>
    );
};

// Важно: Убедитесь, что экспорт именованный
// export default FileUploadSection; // НЕ так
// А так:
// В этом файле экспорт по умолчанию не нужен, так как он не главный файл фичи.
// Поэтому мы оставим его без 'export default' и будем импортировать именовано.