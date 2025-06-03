// frontend/src/features/fileUpload/components/FileUploadList.tsx
import React from 'react';
import { List, Progress, Tag, Typography, Button, Space, Alert } from 'antd';
import {
    CloudUploadOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    LoadingOutlined,
    DeleteOutlined, 
} from '@ant-design/icons';
// ВОЗВРАЩАЕМ ОРИГИНАЛЬНЫЙ ИМПОРТ
import type { UploadProgressInfo } from '../hooks/useFileUploadManager'; 

const { Text } = Typography;

interface FileUploadListProps {
    uploads: UploadProgressInfo[]; // Используем оригинальное имя типа
    // onRemoveFile?: (uid: string) => void;
    // onRetryUpload?: (uid: string) => void;
}

const FileUploadList: React.FC<FileUploadListProps> = ({
    uploads,
    // onRemoveFile,
    // onRetryUpload,
}) => {
    if (uploads.length === 0) {
        return null; 
    }

    const getStatusIconAndColor = (status: UploadProgressInfo['status']) => { // Используем оригинальное имя типа
        switch (status) {
            case 'waiting':
                return { icon: <CloudUploadOutlined />, color: 'default' };
            case 'uploading':
                return { icon: <LoadingOutlined spin />, color: 'processing' };
            case 'accepted': 
                return { icon: <CheckCircleOutlined />, color: 'warning' }; 
            case 'success': 
                return { icon: <CheckCircleOutlined />, color: 'success' };
            case 'error':
                return { icon: <CloseCircleOutlined />, color: 'error' };
            default:
                return { icon: <CloudUploadOutlined />, color: 'default' };
        }
    };

    return (
        <div style={{ marginTop: '20px', maxHeight: '300px', overflowY: 'auto' }}>
            <List
                itemLayout="horizontal"
                dataSource={uploads} 
                renderItem={(item) => { 
                    const { icon, color } = getStatusIconAndColor(item.status);
                    return (
                        <List.Item
                        >
                            <List.Item.Meta
                                avatar={icon}
                                title={<Text style={{ wordBreak: 'break-all' }}>{item.name}</Text>}
                                description={
                                    <>
                                        <Tag color={color} style={{ marginRight: 8 }}>
                                            {item.status === 'waiting' && 'Ожидание'}
                                            {item.status === 'uploading' && 'Загрузка'}
                                            {item.status === 'accepted' && 'Принят (Обработка)'}
                                            {item.status === 'success' && 'Успешно'}
                                            {item.status === 'error' && 'Ошибка'}
                                        </Tag>
                                        {item.status === 'uploading' && item.percent !== undefined && (
                                            <Progress percent={item.percent} size="small" style={{ width: '70%' }} />
                                        )}
                                        {item.status === 'error' && item.errorMessage && (
                                            <Text type="danger" style={{ display: 'block', fontSize: '0.85em' }}>
                                                {item.errorMessage}
                                            </Text>
                                        )}
                                        {item.status === 'accepted' && item.response?.document_id && (
                                            <Text type="secondary" style={{ fontSize: '0.85em' }}>
                                                ID Документа: {item.response.document_id}
                                            </Text>
                                        )}
                                    </>
                                }
                            />
                        </List.Item>
                    );
                }}
            />
        </div>
    );
};

export default FileUploadList;