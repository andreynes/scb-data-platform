/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_for_access_token_api_v1_auth_token_post } from '../models/Body_login_for_access_token_api_v1_auth_token_post';
import type { TokenSchema } from '../models/TokenSchema';
import type { UserCreateSchema } from '../models/UserCreateSchema';
import type { UserSchema } from '../models/UserSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Получение JWT токена
     * Стандартный эндпоинт OAuth2 для получения токена по имени пользователя и паролю.
     * Данные передаются в формате `application/x-www-form-urlencoded`.
     * @returns TokenSchema Successful Response
     * @throws ApiError
     */
    public static loginForAccessTokenApiV1AuthTokenPost({
        formData,
    }: {
        formData: Body_login_for_access_token_api_v1_auth_token_post,
    }): CancelablePromise<TokenSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/token',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Регистрация нового пользователя
     * Создает нового пользователя.
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static registerUserApiV1AuthRegisterPost({
        requestBody,
    }: {
        requestBody: UserCreateSchema,
    }): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Получение данных текущего пользователя
     * Возвращает данные текущего аутентифицированного пользователя.
     * @returns UserSchema Successful Response
     * @throws ApiError
     */
    public static readUsersMeApiV1AuthMeGet(): CancelablePromise<UserSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/me',
        });
    }
}
