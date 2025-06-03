/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Схема для статуса загрузки одного файла.
 * Возвращается API как часть списка после запроса на загрузку файлов.
 */
export type FileUploadStatusSchema = {
    /**
     * Имя загруженного файла
     */
    filename: string;
    /**
     * Уникальный ID, присвоенный документу в системе (ОЗЕРЕ)
     */
    document_id?: string;
    /**
     * Начальный статус обработки файла (например, 'Accepted', 'Processing', 'Error')
     */
    status: string;
    /**
     * Сообщение об ошибке, если что-то пошло не так на этапе приема файла
     */
    error_message?: (string | null);
};

