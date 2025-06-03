/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_files_api_v1_files_upload_post } from '../models/Body_upload_files_api_v1_files_upload_post';
import type { FileUploadStatusSchema } from '../models/FileUploadStatusSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FilesService {
    /**
     * Загрузка одного или нескольких файлов
     * Принимает один или несколько файлов, сохраняет их и инициирует ETL-обработку.
     * @returns FileUploadStatusSchema Successful Response
     * @throws ApiError
     */
    public static uploadFilesApiV1FilesUploadPost({
        formData,
    }: {
        formData: Body_upload_files_api_v1_files_upload_post,
    }): CancelablePromise<Array<FileUploadStatusSchema>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/files/upload',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
