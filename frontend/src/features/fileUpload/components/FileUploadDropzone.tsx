// frontend/src/features/fileUpload/components/FileUploadDropzone.tsx
import React from 'react';
import { Upload, message, Typography, theme } from 'antd';
import type { UploadProps, RcFile } from 'antd/es/upload';
import { InboxOutlined } from '@ant-design/icons';

const { Dragger } = Upload;
const { Title, Text } = Typography;

interface FileUploadDropzoneProps {
    onUploadStart: (files: RcFile[]) => Promise<void> | void; // Функция из хука useFileUploadManager
    acceptedFileTypes?: string[]; // Массив MIME-типов или расширений
    multiple?: boolean;
    disabled?: boolean;
    maxFileSize?: number; // Максимальный размер файла в байтах для клиентской валидации
}

const FileUploadDropzone: React.FC<FileUploadDropzoneProps> = ({
    onUploadStart,
    acceptedFileTypes = ['.xlsx', '.xls', '.pdf'], // Значения по умолчанию для MVP
    multiple = true,
    disabled = false,
    maxFileSize, // например, 5 * 1024 * 1024 для 5MB
}) => {
    const { token } = theme.useToken(); // Для стилизации, если нужно

    const draggerProps: UploadProps = {
        name: 'files', // Имя поля, может быть не важно, если customRequest/beforeUpload
        multiple: multiple,
        accept: acceptedFileTypes.join(','),
        disabled: disabled,
        // Важно: мы не хотим, чтобы Ant Design Upload сам отправлял файлы.
        // Мы перехватываем файлы в beforeUpload и передаем их в onUploadStart.
        beforeUpload: (file, fileList) => {
            // Валидация типа файла (Ant Design делает базовую по accept, но можно усилить)
            const isValidType = acceptedFileTypes.some(type =>
                file.name.toLowerCase().endsWith(type.toLowerCase()) || file.type === type
            );
            if (!isValidType) {
                message.error(`${file.name}: Неподдерживаемый тип файла.`);
                return Upload.LIST_IGNORE; // Не добавлять в список и не загружать
            }

            // Валидация размера файла (клиентская)
            if (maxFileSize && file.size > maxFileSize) {
                message.error(
                    `${file.name}: Файл слишком большой (максимум: ${Math.round(maxFileSize / 1024 / 1024)}MB).`
                );
                return Upload.LIST_IGNORE;
            }
            
            // Если это первый файл в пакете, инициируем загрузку всего пакета
            // Antd вызывает beforeUpload для каждого файла индивидуально.
            // Мы будем собирать все файлы и вызывать onUploadStart один раз.
            // Для этого лучше всего передавать все выбранные файлы сразу.
            // Upload.Dragger передает все файлы в fileList, если multiple=true.
            // Однако, если мы хотим вызывать onUploadStart только ОДИН РАЗ для ПАКЕТА файлов,
            // то стандартный beforeUpload (который вызывается для каждого файла) не очень подходит.
            // Более правильный подход - использовать customRequest или обрабатывать fileList 
            // в onChange, но для MVP и вызова onUploadStart извне, beforeUpload может быть проще,
            // если мы вызовем onUploadStart(fileList) и вернем false для всех, чтобы предотвратить
            // стандартную загрузку AntD.
            
            // Вызываем onUploadStart для ВСЕХ выбранных файлов (fileList)
            // но только если это первый файл из пакета, чтобы избежать многократных вызовов.
            // Это немного "хак", более чистое решение - через onChange и ручное управление списком.
            // Для MVP, если onUploadStart идемпотентен или мы передаем один файл за раз, можно проще.
            
            // ПРОСТОЙ ВАРИАНТ ДЛЯ MVP: передаем файлы по одному через onUploadStart.
            // Хук useFileUploadManager должен быть готов к этому или мы адаптируем хук.
            // Либо FileUploadDropzone должен сам агрегировать файлы и вызывать onUploadStart один раз.

            // Давайте предположим, что onUploadStart ожидает массив файлов.
            // И мы вызываем его для каждого файла отдельно (или для всего списка, если это первый файл).
            // Для упрощения, пусть наш onUploadStart в хуке будет готов принять один файл или массив.
            // В нашем хуке handleUploadStart принимает RcFile[]
            // Если мы хотим вызвать его один раз для всех файлов, то нужно это сделать хитро.
            // Либо передать fileList и убедиться, что onUploadStart вызывается один раз.
            
            // Вариант: вызываем onUploadStart для всего списка файлов, но только для первого файла в списке.
            // Это предотвратит множественные вызовы onUploadStart для одной и той же группы файлов.
            if (file === fileList[0]) {
                onUploadStart(fileList);
            }

            return false; // Всегда возвращаем false, чтобы предотвратить автоматическую загрузку Ant Design
        },
        showUploadList: false, // Мы будем использовать наш кастомный FileUploadList
        style: {
            background: token.colorBgContainerDisabled, // Пример стилизации
            border: `2px dashed ${token.colorBorder}`,
            padding: '40px 20px',
            opacity: disabled ? 0.5 : 1,
        },
        // Можно убрать action, если beforeUpload всегда возвращает false
        // action: "https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188", // Заглушка
    };

    return (
        <Dragger {...draggerProps}>
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

export default FileUploadDropzone;