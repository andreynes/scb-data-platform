// frontend/src/features/fileUpload/components/FileUploadList.tsx

import React from 'react';
import { List, Progress, Tag, Typography, Tooltip } from 'antd';
import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    SyncOutlined,
    ClockCircleOutlined,
    FileDoneOutlined,
    FileSyncOutlined, 
} from '@ant-design/icons';
// Предполагаем, что этот тип определен в хуке или в общем файле типов для фичи
import { UploadProgressInfo } from '../hooks/useFileUploadManager';

const { Text } = Typography;

interface FileUploadListProps {
    uploads: UploadProgressInfo[];
}

// ИЗМЕНЕНИЕ: Мы меняем экспорт на именованный (named export)
export const FileUploadList: React.FC<FileUploadListProps> = ({ uploads }) => {
    // Если нет файлов для отображения, ничего не рендерим
    if (uploads.length === 0) {
        return null;
    }

    const renderStatus = (item: UploadProgressInfo) => {
        switch (item.status) {
            case 'waiting':
                return <Tag icon={<ClockCircleOutlined />} color="default">Ожидание</Tag>;
            case 'uploading':
                return <Progress percent={item.percent} size="small" status="active" />;
            case 'accepted': // Бэкенд принял файл, ждем ETL
                return <Tag icon={<FileSyncOutlined spin />} color="processing">В обработке</Tag>;
            case 'success':
                return <Tag icon={<CheckCircleOutlined />} color="success">Успешно</Tag>;
            case 'error':
                return (
                    <Tooltip title={item.errorMessage}>
                        <Tag icon={<CloseCircleOutlined />} color="error">Ошибка</Tag>
                    </Tooltip>
                );
            default:
                return null;
        }
    };

    return (
        <List
            header={<strong>История загрузок</strong>}
            bordered
            dataSource={uploads}
            renderItem={(item) => (
                <List.Item>
                    <List.Item.Meta
                        avatar={<FileDoneOutlined style={{ fontSize: '24px' }}/>}
                        title={<Text style={{ fontSize: '14px' }}>{item.name}</Text>}
                        description={
                            item.status === 'error' 
                                ? <Text type="danger" style={{ fontSize: '12px' }}>{item.errorMessage}</Text> 
                                : <Text type="secondary" style={{ fontSize: '12px' }}>{`Статус: ${item.status}`}</Text>
                        }
                    />
                    <div style={{ minWidth: '120px', textAlign: 'right' }}>
                        {renderStatus(item)}
                    </div>
                </List.Item>
            )}
        />
    );
};