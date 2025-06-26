/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ReparseRequestSchema = {
    /**
     * Список ID документов для репарсинга
     */
    document_ids: Array<string>;
    /**
     * Версия онтологии для репарсинга (если не указана - активная)
     */
    ontology_version?: (string | null);
};

