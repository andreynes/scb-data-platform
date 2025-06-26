/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrectionInfo } from './CorrectionInfo';
import type { VerificationStatusEnum } from './VerificationStatusEnum';
/**
 * Схема для отправки результата верификации на бэкенд.
 */
export type VerificationResultSchema = {
    document_id: string;
    final_status: VerificationStatusEnum;
    /**
     * Список внесенных исправлений.
     */
    corrections: Array<CorrectionInfo>;
};

