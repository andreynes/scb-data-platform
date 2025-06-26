/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Схема для одной задачи в очереди на верификацию.
 */
export type VerificationTaskSchema = {
    document_id: string;
    filename: string;
    source: string;
    upload_timestamp: string;
    reason_for_verification: string;
    priority_score?: (number | null);
};

