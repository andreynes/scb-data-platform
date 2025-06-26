/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { VerificationDataSchema } from '../models/VerificationDataSchema';
import type { VerificationResultSchema } from '../models/VerificationResultSchema';
import type { VerificationTaskSchema } from '../models/VerificationTaskSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VerificationService {
    /**
     * Получение очереди задач на верификацию
     * Возвращает список задач, ожидающих ручной верификации.
     * @returns VerificationTaskSchema Successful Response
     * @throws ApiError
     */
    public static getVerificationQueueApiV1AdminVerificationQueueGet({
        limit = 50,
        offset,
    }: {
        /**
         * Максимальное количество задач
         */
        limit?: number,
        /**
         * Смещение для пагинации
         */
        offset?: number,
    }): CancelablePromise<Array<VerificationTaskSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/verification/queue',
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Получение данных для конкретной задачи верификации
     * Возвращает данные (JSON и атомы) для указанной задачи верификации.
     * @returns VerificationDataSchema Successful Response
     * @throws ApiError
     */
    public static getVerificationTaskDataApiV1AdminVerificationTaskIdDataGet({
        taskId,
    }: {
        taskId: string,
    }): CancelablePromise<VerificationDataSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/verification/{task_id}/data',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Отправка результата ручной верификации
     * Принимает и сохраняет результат верификации (статус и исправления).
     * @returns void
     * @throws ApiError
     */
    public static submitVerificationResultApiV1AdminVerificationSubmitPost({
        requestBody,
    }: {
        requestBody: VerificationResultSchema,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/admin/verification/submit',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
