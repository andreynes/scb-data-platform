/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OntologySchema } from '../models/OntologySchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OntologyService {
    /**
     * Получить текущую активную схему онтологии
     * Возвращает полную структуру текущей активной версии онтологии, включая атрибуты, их типы, описания и иерархии.
     * @returns OntologySchema Successful Response
     * @throws ApiError
     */
    public static getCurrentOntologySchemaApiV1OntologySchemaGet(): CancelablePromise<OntologySchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ontology/schema',
            errors: {
                404: `Активная схема онтологии не найдена`,
                500: `Внутренняя ошибка сервера`,
            },
        });
    }
}
