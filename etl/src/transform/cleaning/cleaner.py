# etl/src/transform/cleaning/cleaner.py
import re
from typing import List, Dict, Any, Optional

def clean_string_value(value: Any) -> Optional[str]:
    """Базовая очистка строкового значения: удаляет лишние пробелы."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value) # Пытаемся преобразовать в строку, если это не строка
    
    cleaned_value = value.strip()
    # Заменяем множественные пробелы на один
    cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
    return cleaned_value if cleaned_value else None # Возвращаем None, если строка стала пустой

def standardize_numeric_string(value: Any) -> Optional[str]:
    """
    Подготавливает строку, которая может содержать число, к парсингу.
    Удаляет символы валют, пробелы (как разделители тысяч), заменяет запятую на точку.
    """
    if value is None:
        return None
    s_value = str(value).strip()
    
    # Удаляем известные символы валют (можно расширить)
    s_value = s_value.replace('₽', '').replace('$', '').replace('€', '')
    # Удаляем пробелы (которые могут быть разделителями тысяч)
    s_value = s_value.replace(' ', '')
    # Заменяем запятую на точку для десятичных чисел
    s_value = s_value.replace(',', '.')
    
    # Оставляем только цифры, точку, и минус в начале
    # Этот regex может быть сложным, если числа имеют разные форматы
    # Простой вариант: удалить все, кроме цифр, точки и минуса
    # cleaned_value = re.sub(r'[^\d.\-]', '', s_value) 
    # Более строгий вариант для чисел типа -123.45 или 123 или .45
    match = re.search(r'-?(\d+\.?\d*|\.\d+)', s_value)
    if match:
        return match.group(0)
    return None # Если не похоже на число после очистки

def normalize_header_name(name: str) -> str:
    """
    Нормализует имя заголовка/ключа: нижний регистр, замена пробелов/спецсимволов на _.
    """
    if not isinstance(name, str):
        name = str(name)
    name = name.lower()
    name = re.sub(r'\s+', '_', name) # Заменяем пробелы на _
    name = re.sub(r'[^\w_]+', '', name) # Удаляем все не-буквенно-цифровые символы, кроме _
    name = re.sub(r'_+', '_', name) # Заменяем множественные _ на один
    name = name.strip('_') # Удаляем _ в начале и конце
    return name

def clean_parsed_data(
    parsed_data: List[Dict[str, Any]],
    ontology_schema: Dict[str, Any] # Для определения ожидаемых типов и применения нужной очистки
) -> List[Dict[str, Any]]:
    """
    Очищает распарсенные данные.
    Нормализует ключи словарей (заголовки).
    Применяет очистку значений в зависимости от типа, указанного в онтологии.
    """
    cleaned_data_list: List[Dict[str, Any]] = []
    if not ontology_schema or not ontology_schema.get('attributes'):
        logger.warning("Ontology schema or attributes not provided for cleaning. Skipping type-specific cleaning.")
        # Если онтологии нет, просто нормализуем ключи и базово чистим строки
        for row in parsed_data:
            cleaned_row = {normalize_header_name(k): clean_string_value(v) for k, v in row.items()}
            cleaned_data_list.append(cleaned_row)
        return cleaned_data_list

    # Создаем маппинг нормализованных имен атрибутов онтологии на их типы
    ontology_attribute_types = {
        attr['name']: attr.get('type', 'string') 
        for attr in ontology_schema.get('attributes', [])
    }
    
    for raw_row in parsed_data:
        cleaned_row: Dict[str, Any] = {}
        for raw_key, raw_value in raw_row.items():
            normalized_key = normalize_header_name(raw_key)
            
            # Пропускаем ключи, которых нет в онтологии (или решить как их обрабатывать)
            if normalized_key not in ontology_attribute_types:
                # logger.debug(f"Header '{raw_key}' (normalized to '{normalized_key}') not found in ontology. Skipping.")
                continue

            expected_type = ontology_attribute_types.get(normalized_key, 'string')
            
            cleaned_value = raw_value
            if expected_type in ['integer', 'float', 'decimal']: # Decimal добавим позже
                cleaned_value = standardize_numeric_string(raw_value)
            elif expected_type == 'string':
                cleaned_value = clean_string_value(raw_value)
            # Для 'date', 'datetime', 'boolean' базовая строковая очистка может быть достаточной,
            # основная работа будет в валидаторе/преобразователе типов
            elif expected_type in ['date', 'datetime', 'boolean']:
                 cleaned_value = clean_string_value(raw_value) # Базовая очистка
            
            cleaned_row[normalized_key] = cleaned_value
        
        # Добавляем только если строка не стала пустой после очистки и фильтрации по онтологии
        if cleaned_row:
            cleaned_data_list.append(cleaned_row)
    
    return cleaned_data_list

# Пример логгера (если вынесли setup_etl_logger)
from ...utils.logging_utils import setup_etl_logger
logger = setup_etl_logger(__name__)

if __name__ == '__main__':
    test_parsed_data = [
        {"Наименование Товара": "  Молоко 3.2%  ", " Цена, РУБ ": "  123,45 руб.  ", "  Город Продажи  ": "Москва"},
        {"Наименование Товара": "Хлеб   Бородинский", " Цена, РУБ ": "50", "Неизвестное Поле": "значение"}
    ]
    # Упрощенная онтология для теста
    test_ontology = {
        "attributes": [
            {"name": "product_name", "type": "string", "description": "Наименование Товара"},
            {"name": "price_rub", "type": "float", "description": "Цена, РУБ"},
            {"name": "sale_city", "type": "string", "description": "Город Продажи"}
        ]
    }
    print("--- Testing clean_parsed_data ---")
    cleaned = clean_parsed_data(test_parsed_data, test_ontology)
    for row in cleaned:
        print(row)
    
    # {'product_name': 'Молоко 3.2%', 'price_rub': '123.45', 'sale_city': 'Москва'}
    # {'product_name': 'Хлеб Бородинский', 'price_rub': '50'}
    
    print(f"\n--- normalize_header_name('  Код ОКАТО (новый)  ') -> {normalize_header_name('  Код ОКАТО (новый)  ')}")
    #  -> kod_okato_novyj
    print(f"--- standardize_numeric_string('  1 234,56 $ ') -> {standardize_numeric_string('  1 234,56 $ ')}")
    #  -> 1234.56
    print(f"--- clean_string_value('  много   пробелов  ') -> {clean_string_value('  много   пробелов  ')}")
    #  -> много пробелов