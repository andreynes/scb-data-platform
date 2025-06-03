// frontend/src/features/fileUpload/components/FileUploadSection.tsx
import React from 'react';
import { Card, Button, Space, Typography } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { useFileUploadManager } from '../hooks/useFileUploadManager';
import FileUploadDropzone from './FileUploadDropzone';
import FileUploadList from './FileUploadList';

const { Title } = Typography;

interface FileUploadSectionProps {
    // Можно добавить пропсы для кастомизации, если нужно, например:
    // acceptedFileTypes?: string[];
    // maxFileSize?: number;
    // showClearButton?: boolean;
}

const FileUploadSection: React.FC<FileUploadSectionProps> = (props) => {
    const {
        uploads,
        handleUploadStart,
        clearCompletedUploads,
    } = useFileUploadManager();

    const hasActiveUploads = uploads.some(
        up => up.status === 'uploading' || up.status === 'waiting'
    );
    const hasCompletedOrFailedUploads = uploads.some(
        up => up.status === 'success' || up.status === 'accepted' || up.status === 'error'
    );

    return (
        <Card title={<Title level={3}>Загрузка файлов</Title>}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
                <FileUploadDropzone
                    onUploadStart={handleUploadStart}
                    // Передаем пропсы дальше, если они есть
                    // acceptedFileTypes={props.acceptedFileTypes}
                    // maxFileSize={props.maxFileSize}
                    disabled={hasActiveUploads} // Блокируем дропзону во время активных загрузок
                />

                {uploads.length > 0 && (
                    <FileUploadList uploads={uploads} />
                )}

                {hasCompletedOrFailedUploads && !hasActiveUploads && (
                    <Button
                        icon={<DeleteOutlined />}
                        onClick={clearCompletedUploads}
                        danger
                        style={{ marginTop: '10px' }}
                    >
                        Очистить завершенные
                    </Button>
                )}
            </Space>
        </Card>
    );
};

export default FileUploadSection;