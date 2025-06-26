/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataQueryResponseSchema } from '../models/DataQueryResponseSchema';
import type { DataQuerySchema } from '../models/DataQuerySchema';
import type { ExportFormat } from '../models/ExportFormat';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DataService {
    /**
     * Запрос атомарных данных из СКЛАДА
     * Принимает ID документа и возвращает все связанные с ним атомарные записи данных из СКЛАДА (ClickHouse).
     *
     * Требует аутентификации.
     * @returns DataQueryResponseSchema Successful Response
     * @throws ApiError
     */
    public static queryDataApiV1DataQueryPost({
        requestBody,
    }: {
        requestBody: DataQuerySchema,
    }): CancelablePromise<DataQueryResponseSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/query',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Данные для указанного ID документа не найдены`,
                422: `Validation Error`,
                500: `Внутренняя ошибка сервера`,
            },
        });
    }
    /**
     * Запрос атомарных данных из СКЛАДА
     * Принимает ID документа и возвращает все связанные с ним атомарные записи данных из СКЛАДА (ClickHouse).
     *
     * Требует аутентификации.
     * @returns DataQueryResponseSchema Successful Response
     * @throws ApiError
     */
    public static queryDataApiV1DataQueryPost1({
        requestBody,
    }: {
        requestBody: DataQuerySchema,
    }): CancelablePromise<DataQueryResponseSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/query',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Данные для указанного ID документа не найдены`,
                422: `Validation Error`,
                500: `Внутренняя ошибка сервера`,
            },
        });
    }
    /**
     * Экспорт данных в файл
     * Формирует и возвращает файл (Excel или CSV) с данными по заданным параметрам запроса.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportDataApiV1DataExportPost({
        format,
        requestBody,
    }: {
        /**
         * Формат экспорта: 'excel' или 'csv'
         */
        format: ExportFormat,
        requestBody: DataQuerySchema,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/export',
            query: {
                'format': format,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Данные для экспорта по указанным параметрам не найдены`,
                422: `Validation Error`,
                500: `Внутренняя ошибка сервера при создании файла`,
            },
        });
    }
    /**
     * Экспорт данных в файл
     * Формирует и возвращает файл (Excel или CSV) с данными по заданным параметрам запроса.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportDataApiV1DataExportPost1({
        format,
        requestBody,
    }: {
        /**
         * Формат экспорта: 'excel' или 'csv'
         */
        format: ExportFormat,
        requestBody: DataQuerySchema,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/export',
            query: {
                'format': format,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Данные для экспорта по указанным параметрам не найдены`,
                422: `Validation Error`,
                500: `Внутренняя ошибка сервера при создании файла`,
            },
        });
    }
    /**
     * Пометить документ для ручной верификации ("Тревожная кнопка")
     * Устанавливает документу статус 'Needs Verification', чтобы он появился в очереди на проверку у Мейнтейнера. Требует аутентификации.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static flagForVerificationApiV1DataDocumentIdFlagForVerificationPost({
        documentId,
    }: {
        documentId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/{document_id}/flag-for-verification',
            path: {
                'document_id': documentId,
            },
            errors: {
                404: `Документ с указанным ID не найден`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Пометить документ для ручной верификации ("Тревожная кнопка")
     * Устанавливает документу статус 'Needs Verification', чтобы он появился в очереди на проверку у Мейнтейнера. Требует аутентификации.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static flagForVerificationApiV1DataDocumentIdFlagForVerificationPost1({
        documentId,
    }: {
        documentId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/data/{document_id}/flag-for-verification',
            path: {
                'document_id': documentId,
            },
            errors: {
                404: `Документ с указанным ID не найден`,
                422: `Validation Error`,
            },
        });
    }
}
