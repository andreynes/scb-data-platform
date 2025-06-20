// frontend/src/features/fileUpload/components/FileUploadDropzone.tsx
import React from 'react';
import { Upload, message, Typography, theme } from 'antd';
import type { UploadProps, RcFile } from 'antd/es/upload';
import { InboxOutlined } from '@ant-design/icons';

const { Dragger } = Upload;
const { Title, Text } = Typography;

// Определяем интерфейс для пропсов компонента
interface FileUploadDropzoneProps {
    onUploadStart: (files: RcFile[]) => void; // Функция из хука-менеджера
    acceptedFileTypes?: string[]; // Массив MIME-типов или расширений
    multiple?: boolean;
    disabled?: boolean;
    maxFileSize?: number; // Максимальный размер файла в байтах для клиентской валидации
}

// ИЗМЕНЕНИЕ 1: Мы меняем экспорт на именованный (named export)
// Это решает ошибку, которую вы видите на скриншоте.
export const FileUploadDropzone: React.FC<FileUploadDropzoneProps> = ({
    onUploadStart,
    acceptedFileTypes = ['.xlsx', '.xls', '.pdf'], // Значения по умолчанию для MVP
    multiple = true,
    disabled = false,
    maxFileSize, // например, 5 * 1024 * 1024 для 5MB
}) => {
    const { token } = theme.useToken(); // Для стилизации, если нужно

    const draggerProps: UploadProps = {
        name: 'files',
        multiple: multiple,
        accept: acceptedFileTypes.join(','),
        disabled: disabled,

        // Важно: мы не хотим, чтобы Ant Design Upload сам отправлял файлы.
        // Мы перехватываем файлы в beforeUpload и передаем их в onUploadStart.
        beforeUpload: (file, fileList) => {
            // Валидация типа файла
            const isValidType = acceptedFileTypes.some(type =>
                file.name.toLowerCase().endsWith(type.toLowerCase()) || file.type === type
            );
            if (!isValidType) {
                message.error(`${file.name}: Неподдерживаемый тип файла.`);
                return Upload.LIST_IGNORE;
            }

            // Валидация размера файла
            if (maxFileSize && file.size > maxFileSize) {
                message.error(
                    `${file.name}: Файл слишком большой (максимум: ${Math.round(maxFileSize / 1024 / 1024)}MB).`
                );
                return Upload.LIST_IGNORE;
            }
            
            // ИЗМЕНЕНИЕ 2: Упрощаем логику. Вызываем onUploadStart для всего списка выбранных файлов.
            // Это более надежно, чем отслеживать первый файл.
            // onUploadStart будет вызван один раз для группы файлов.
            onUploadStart(fileList);
            
            // Всегда возвращаем false, чтобы предотвратить автоматическую загрузку от Ant Design.
            // Мы полностью управляем процессом загрузки сами.
            return false;
        },
        showUploadList: false, // Мы используем наш кастомный FileUploadList для отображения статуса
    };

    // Стили для наглядности вынесены в константу
    const draggerStyle: React.CSSProperties = {
        background: disabled ? token.colorBgContainerDisabled : token.colorBgContainer,
        border: `2px dashed ${token.colorBorder}`,
        padding: '40px 20px',
        opacity: disabled ? 0.5 : 1,
        transition: 'opacity 0.3s',
    };

    return (
        <Dragger {...draggerProps} style={draggerStyle}>
            <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ fontSize: '48px', color: token.colorPrimary }} />
            </p>
            <Title level={4} style={{ marginBottom: 4 }}>
                Нажмите или перетащите файлы для загрузки
            </Title>
            <Text type="secondary">
                Поддерживаются файлы Excel (.xlsx, .xls) и PDF (.pdf).
                {maxFileSize && ` Максимальный размер файла: ${Math.round(maxFileSize / 1024 / 1024)}MB.`}
            </Text>
        </Dragger>
    );
};