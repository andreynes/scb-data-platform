/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ApiRequestOptions } from './ApiRequestOptions';

// Типы остаются без изменений
type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;
type Headers = Record<string, string>;

export type OpenAPIConfig = {
    BASE: string;
    VERSION: string;
    WITH_CREDENTIALS: boolean;
    CREDENTIALS: 'include' | 'omit' | 'same-origin';
    TOKEN?: string | Resolver<string> | undefined;
    USERNAME?: string | Resolver<string> | undefined;
    PASSWORD?: string | Resolver<string> | undefined;
    HEADERS?: Headers | Resolver<Headers> | undefined;
    ENCODE_PATH?: ((path: string) => string) | undefined;
};

// --- ОСНОВНЫЕ ИЗМЕНЕНИЯ ЗДЕСЬ ---
export const OpenAPI: OpenAPIConfig = {
    // Базовый URL теперь не нужен, так как он обрабатывается прокси в apiClient
    BASE: '', 
    VERSION: '1.0.0',
    WITH_CREDENTIALS: false,
    CREDENTIALS: 'include',
    
    // КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: 
    // Мы предоставляем функцию (Resolver), которая будет динамически
    // получать токен из localStorage перед каждым запросом.
    // Сгенерированный код автоматически добавит заголовок "Authorization: Bearer <результат_этой_функции>".
    TOKEN: async () => {
        return localStorage.getItem('authToken');
    },

    // Остальные поля можно оставить по умолчанию
    USERNAME: undefined,
    PASSWORD: undefined,
    HEADERS: undefined,
    ENCODE_PATH: undefined,
};