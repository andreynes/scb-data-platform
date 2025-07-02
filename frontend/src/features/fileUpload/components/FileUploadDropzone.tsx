// Файл: frontend/src/features/fileUpload/components/FileUploadDropzone.tsx

import React from 'react';
import { Upload, message, Typography, theme } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps, RcFile } from 'antd/es/upload';

const { Dragger } = Upload;
const { Title, Text } = Typography;

// Определяем пропсы для нашего кастомного компонента
interface FileUploadDropzoneProps {
    onUploadStart: (files: RcFile[]) => void;
    acceptedFileTypes?: string[];
    multiple?: boolean;
    disabled?: boolean;
    maxFileSize?: number; // в байтах
}

const FileUploadDropzone: React.FC<FileUploadDropzoneProps> = ({
    onUploadStart,
    acceptedFileTypes = ['.xlsx', '.xls', '.pdf'],
    multiple = true,
    disabled = false,
    maxFileSize,
}) => {
    const { token } = theme.useToken();

    const props: UploadProps = {
        name: 'files',
        multiple: multiple,
        accept: acceptedFileTypes.join(','),
        disabled: disabled,
        // Мы используем beforeUpload для перехвата файлов, т.к. управляем загрузкой извне
        beforeUpload: (file, fileList) => {
            // Валидация размера файла
            if (maxFileSize && file.size > maxFileSize) {
                message.error(`${file.name}: Файл слишком большой (максимум: ${maxFileSize / 1024 / 1024} MB).`);
                return Upload.LIST_IGNORE; // Отменяем загрузку этого файла
            }
            
            // Если это первый файл в пакете, вызываем onUploadStart со всем списком
            if (file === fileList[0]) {
                onUploadStart(fileList);
            }
            
            // Возвращаем false, чтобы предотвратить автоматическую загрузку от Ant Design
            return false;
        },
        // Мы не хотим показывать стандартный список файлов Ant Design
        showUploadList: false,
    };

    const draggerStyle: React.CSSProperties = {
        background: token.colorBgContainerDisabled,
        border: `2px dashed ${token.colorBorder}`,
        padding: '40px 20px',
        textAlign: 'center',
        opacity: disabled ? 0.5 : 1,
    };

    return (
        <Dragger {...props} style={draggerStyle}>
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <Title level={4} style={{ marginBottom: 4 }}>Нажмите или перетащите файлы для загрузки</Title>
            <Text type="secondary">Поддерживаются файлы Excel (.xlsx, .xls) и PDF (.pdf).</Text>
            {maxFileSize && <Text type="secondary" style={{ display: 'block' }}>Максимальный размер файла: {maxFileSize / 1024 / 1024} MB</Text>}
        </Dragger>
    );
};

// === ГЛАВНОЕ ИЗМЕНЕНИЕ: Добавляем экспорт по умолчанию ===
export default FileUploadDropzone;