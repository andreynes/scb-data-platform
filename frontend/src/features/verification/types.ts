// frontend/src/features/verification/types.ts

// Информация о ячейке, которую кликнули
export interface SelectedCellInfo {
  atomId: string;
  columnKey: string;
  currentValue: any;
}

// Информация об одном исправлении
export interface CorrectionInfo {
  atomId: string;
  fieldName: string;
  newValue: any;
}