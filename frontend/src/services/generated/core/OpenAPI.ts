/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

// --- ИМПОРТИРУЕМ ВАШ НАСТРОЕННЫЙ КЛИЕНТ ---
import apiClient from '../../apiClient'; 
import type { ApiRequestOptions } from './ApiRequestOptions';

type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;
type Headers = Record<string, string>;

export type OpenAPIConfig = {
    // --- ДОБАВЛЯЕМ ПОЛЕ ДЛЯ AXIOS-КЛИЕНТА ---
    CLIENT?: any;
    BASE: string;
    VERSION: string;
    // ... (остальные поля)
};

export const OpenAPI: OpenAPIConfig = {
    // --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: УКАЗЫВАЕМ НАШ КЛИЕНТ ---
    CLIENT: apiClient,

    // BASE URL теперь не нужен, так как он задан в apiClient
    BASE: '', 
    VERSION: '1.0.0',
    // ... (остальные поля остаются как есть)
    WITH_CREDENTIALS: false,
    CREDENTIALS: 'include',
    TOKEN: undefined,
    USERNAME: undefined,
    PASSWORD: undefined,
    HEADERS: undefined,
    ENCODE_PATH: undefined,
};