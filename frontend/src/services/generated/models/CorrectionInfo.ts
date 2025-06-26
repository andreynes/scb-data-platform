/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Схема для одного конкретного исправления, сделанного Мейнтейнером.
 */
export type CorrectionInfo = {
    /**
     * Уникальный ID атома (строки) в СКЛАДЕ, который исправляется.
     */
    atom_id: string;
    /**
     * Техническое имя атрибута (колонки), который исправляется.
     */
    field_name: string;
    /**
     * Новое значение для ячейки.
     */
    new_value: any;
    /**
     * Если Мейнтейнер изменил сопоставление с атрибутом онтологии.
     */
    new_attribute_name?: (string | null);
    /**
     * Если значение помечено как NULL_NOT_APPLICABLE.
     */
    is_not_applicable?: (boolean | null);
    /**
     * Исходное значение (для логирования).
     */
    original_value?: null;
};

