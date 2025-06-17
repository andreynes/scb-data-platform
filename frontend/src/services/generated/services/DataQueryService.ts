/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataQueryResponseSchema } from '../models/DataQueryResponseSchema';
import type { DataQuerySchema } from '../models/DataQuerySchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DataQueryService {
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
}
