/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReparseRequestSchema } from '../models/ReparseRequestSchema';
import type { ReparseResponseSchema } from '../models/ReparseResponseSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EtlService {
    /**
     * Запуск ручного репарсинга документов
     * Инициирует ручной репарсинг для списка документов.
     * Доступно только для пользователей с правами Администратора/Мейнтейнера.
     * @returns ReparseResponseSchema Successful Response
     * @throws ApiError
     */
    public static triggerManualReparseApiV1AdminReparsePost({
        requestBody,
    }: {
        requestBody: ReparseRequestSchema,
    }): CancelablePromise<ReparseResponseSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/admin/reparse',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
