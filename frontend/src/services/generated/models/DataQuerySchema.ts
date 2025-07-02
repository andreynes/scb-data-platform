/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AggregationRule } from './AggregationRule';
import type { FilterCondition } from './FilterCondition';
import type { PaginationParams } from './PaginationParams';
import type { SortRule } from './SortRule';
export type DataQuerySchema = {
    document_id: string;
    filters?: (Array<FilterCondition> | null);
    aggregations?: (Array<AggregationRule> | null);
    columns?: (Array<string> | null);
    sort?: (Array<SortRule> | null);
    pagination?: (PaginationParams | null);
};

