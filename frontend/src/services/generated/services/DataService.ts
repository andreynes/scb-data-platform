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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Запрос атомарных данных из СКЛАДА
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Data
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Data
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Flag For Verification
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Flag For Verification
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
                422: `Validation Error`,
            },
        });
    }
}
