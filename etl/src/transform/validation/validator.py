# etl/src/transform/validation/validator.py
from typing import List, Dict, Any, Tuple, Optional
from .type_validator import is_value_valid_for_type
from .vocabulary_validator import is_value_in_vocabulary
from ...utils.logging_utils import setup_etl_logger # Импортируем наш логгер

logger = setup_etl_logger(__name__)

# Для MVP мы будем просто заменять невалидные значения на None
# и, возможно, собирать информацию об ошибках.
# Более сложная система может возвращать детальные отчеты о валидации.

def validate_cleaned_data(
    cleaned_data: List[Dict[str, Any]],
    ontology_schema: Dict[str, Any],
    ontology_vocabularies: Dict[str, List[Any]],
    original_document_id: str # Для логирования ошибок
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Валидирует очищенные данные на основе схемы онтологии и справочников.

    Args:
        cleaned_data: Список словарей с очищенными данными. 
                      Ключи должны быть уже нормализованы.
        ontology_schema: Словарь, представляющий схему онтологии.
        ontology_vocabularies: Словарь справочников {имя_справочника: [значения]}.
        original_document_id: ID исходного документа для логирования.

    Returns:
        Кортеж из двух списков:
        1. validated_data: Список словарей с данными, где невалидные значения 
                           заменены на None (для MVP).
        2. validation_errors: Список словарей с информацией об ошибках валидации.
                              Каждый словарь может содержать:
                              {'document_id', 'row_index', 'field_name', 'original_value', 'error_type', 'message'}
    """
    validated_data_list: List[Dict[str, Any]] = []
    validation_errors_list: List[Dict[str, Any]] = []

    if not ontology_schema or not ontology_schema.get('attributes'):
        logger.error(f"Ontology schema or attributes not provided for validation of doc_id: {original_document_id}. Returning data as is.")
        return cleaned_data, validation_errors_list # Возвращаем как есть, если нет схемы

    # Создаем маппинг имен атрибутов на их метаданные для быстрого доступа
    attributes_map: Dict[str, Dict[str, Any]] = {
        attr['name']: attr for attr in ontology_schema.get('attributes', [])
    }

    for row_index, row_data in enumerate(cleaned_data):
        validated_row = {}
        is_row_valid = True # Флаг для всей строки (пока не используется, но может пригодиться)

        for field_name, original_value in row_data.items():
            attribute_meta = attributes_map.get(field_name)
            
            current_value = original_value
            is_field_valid = True

            if not attribute_meta:
                # Поле из данных отсутствует в онтологии - пропускаем или логируем?
                # logger.warning(f"Field '{field_name}' in doc_id '{original_document_id}' not found in ontology. Skipping validation for this field.")
                validated_row[field_name] = current_value # Оставляем как есть, или удаляем?
                continue

            expected_type = attribute_meta.get('type')
            vocabulary_name = attribute_meta.get('vocabulary')

            # 1. Валидация типа
            if expected_type and not is_value_valid_for_type(current_value, expected_type):
                error_detail = {
                    "document_id": original_document_id,
                    "row_index": row_index, # Индекс строки в cleaned_data
                    "field_name": field_name,
                    "original_value": original_value,
                    "error_type": "TYPE_MISMATCH",
                    "message": f"Value '{original_value}' is not a valid '{expected_type}'."
                }
                validation_errors_list.append(error_detail)
                logger.debug(f"Validation Error (doc: {original_document_id}, row: {row_index}, field: {field_name}): {error_detail['message']}")
                current_value = None # Для MVP заменяем на None
                is_field_valid = False
                is_row_valid = False
            
            # 2. Валидация по справочнику (только если значение не None и тип прошел)
            if is_field_valid and current_value is not None and vocabulary_name:
                vocabulary_list = ontology_vocabularies.get(vocabulary_name)
                if vocabulary_list is None: # Справочник не найден
                    error_detail = {
                        "document_id": original_document_id,
                        "row_index": row_index,
                        "field_name": field_name,
                        "original_value": current_value, # Используем current_value, т.к. тип уже мог быть преобразован
                        "error_type": "VOCABULARY_NOT_FOUND",
                        "message": f"Vocabulary '{vocabulary_name}' not found for field '{field_name}'."
                    }
                    validation_errors_list.append(error_detail)
                    logger.warning(f"Validation Warning (doc: {original_document_id}, row: {row_index}, field: {field_name}): {error_detail['message']}")
                    # current_value = None # Оставляем значение, но есть предупреждение
                elif not is_value_in_vocabulary(current_value, vocabulary_list):
                    error_detail = {
                        "document_id": original_document_id,
                        "row_index": row_index,
                        "field_name": field_name,
                        "original_value": current_value,
                        "error_type": "NOT_IN_VOCABULARY",
                        "message": f"Value '{current_value}' not in vocabulary '{vocabulary_name}'."
                    }
                    validation_errors_list.append(error_detail)
                    logger.debug(f"Validation Error (doc: {original_document_id}, row: {row_index}, field: {field_name}): {error_detail['message']}")
                    current_value = None # Для MVP заменяем на None
                    is_row_valid = False
            
            validated_row[field_name] = current_value
        
        validated_data_list.append(validated_row)
        
    return validated_data_list, validation_errors_list

if __name__ == '__main__':
    # Пример данных
    test_cleaned_data = [
        {"product_name": "Молоко", "price_rub": "123.45", "sale_city": "Москва", "quantity": "10шт"},
        {"product_name": "Хлеб", "price_rub": "пятьдесят", "sale_city": "СПБ", "quantity": "1"}
    ]
    test_ontology_schema = {
        "version": "1.0",
        "attributes": [
            {"name": "product_name", "type": "string"},
            {"name": "price_rub", "type": "float"},
            {"name": "sale_city", "type": "string", "vocabulary": "cities"},
            {"name": "quantity", "type": "integer"} # quantity нет в примере данных, но есть в онтологии
        ]
    }
    test_ontology_vocabularies = {
        "cities": ["Москва", "Санкт-Петербург", "Новосибирск"]
    }
    doc_id_for_test = "test_doc_123"

    print("--- Testing validate_cleaned_data ---")
    validated_data, errors = validate_cleaned_data(
        test_cleaned_data, 
        test_ontology_schema, 
        test_ontology_vocabularies,
        doc_id_for_test
    )
    
    print("\nValidated Data:")
    for row in validated_data:
        print(row)
    
    print("\nValidation Errors:")
    for error in errors:
        print(error)
    
    # Ожидаемый примерный вывод:
    # Validated Data:
    # {'product_name': 'Молоко', 'price_rub': '123.45', 'sale_city': 'Москва', 'quantity': '10шт'}
    # {'product_name': 'Хлеб', 'price_rub': None, 'sale_city': None, 'quantity': '1'}
    # Validation Errors:
    # {'document_id': 'test_doc_123', 'row_index': 1, 'field_name': 'price_rub', 'original_value': 'пятьдесят', 'error_type': 'TYPE_MISMATCH', 'message': "Value 'пятьдесят' is not a valid 'float'."}
    # {'document_id': 'test_doc_123', 'row_index': 1, 'field_name': 'sale_city', 'original_value': 'СПБ', 'error_type': 'NOT_IN_VOCABULARY', 'message': "Value 'СПБ' not in vocabulary 'cities'."}
    # {'document_id': 'test_doc_123', 'row_index': 0, 'field_name': 'quantity', 'original_value': '10шт', 'error_type': 'TYPE_MISMATCH', 'message': "Value '10шт' is not a valid 'integer'."} 
    # (ошибка для quantity из-за 'шт', если _is_valid_integer строг)