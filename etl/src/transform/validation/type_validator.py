# etl/src/transform/validation/type_validator.py
from typing import Any
from datetime import datetime, date

# Простые форматы дат для парсинга, можно расширить или использовать dateutil.parser
DATE_FORMATS = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]
DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", 
    "%d.%m.%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f", # с микросекундами
]

def _is_valid_integer(value: Any) -> bool:
    if value is None: return True # None считаем валидным на этом этапе, обработка NULL - отдельно
    if isinstance(value, int): return True
    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            return False
    # Попытка конвертировать float, если он целый (e.g., "123.0")
    if isinstance(value, float) and value.is_integer():
        return True
    return False

def _is_valid_float(value: Any) -> bool:
    if value is None: return True
    if isinstance(value, (int, float)): return True # int тоже валидный float
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False

def _is_valid_date_or_datetime(value: Any, expected_type: str) -> bool:
    if value is None: return True
    if expected_type == 'date' and isinstance(value, date) and not isinstance(value, datetime): return True
    if expected_type == 'datetime' and isinstance(value, datetime): return True
    
    if isinstance(value, str):
        formats_to_try = DATETIME_FORMATS if expected_type == 'datetime' else DATE_FORMATS
        for fmt in formats_to_try:
            try:
                dt_obj = datetime.strptime(value, fmt)
                if expected_type == 'date' and dt_obj.time() == datetime.min.time():
                    return True
                elif expected_type == 'datetime':
                    return True
            except ValueError:
                continue
    return False

def _is_valid_boolean(value: Any) -> bool:
    if value is None: return True
    if isinstance(value, bool): return True
    if isinstance(value, str):
        return value.lower() in ['true', 'false', '1', '0', 'да', 'нет', 'yes', 'no']
    if isinstance(value, int) and value in [0, 1]:
        return True
    return False

def is_value_valid_for_type(value: Any, expected_type: str) -> bool:
    """
    Проверяет, соответствует ли значение ожидаемому типу данных из онтологии.
    None считается валидным на этом этапе.
    """
    if value is None: # Обработка NULL происходит в null_handler
        return True

    if expected_type == 'string':
        return isinstance(value, (str, int, float, bool)) # Почти все можно привести к строке
    elif expected_type == 'integer':
        return _is_valid_integer(value)
    elif expected_type == 'float': # или 'decimal'
        return _is_valid_float(value)
    elif expected_type == 'date':
        return _is_valid_date_or_datetime(value, 'date')
    elif expected_type == 'datetime':
        return _is_valid_date_or_datetime(value, 'datetime')
    elif expected_type == 'boolean':
        return _is_valid_boolean(value)
    else:
        # logger.warning(f"Unknown expected type: {expected_type} for value: {value}")
        return False # Неизвестный тип не может быть валидирован

if __name__ == '__main__':
    print(f"is_value_valid_for_type('123', 'integer'): {is_value_valid_for_type('123', 'integer')}") # True
    print(f"is_value_valid_for_type('123.0', 'integer'): {is_value_valid_for_type('123.0', 'integer')}") # True
    print(f"is_value_valid_for_type('123.45', 'integer'): {is_value_valid_for_type('123.45', 'integer')}")# False
    print(f"is_value_valid_for_type('123.45', 'float'): {is_value_valid_for_type('123.45', 'float')}") # True
    print(f"is_value_valid_for_type('abc', 'float'): {is_value_valid_for_type('abc', 'float')}")       # False
    print(f"is_value_valid_for_type('2023-10-27', 'date'): {is_value_valid_for_type('2023-10-27', 'date')}") # True
    print(f"is_value_valid_for_type('27.10.2023', 'date'): {is_value_valid_for_type('27.10.2023', 'date')}") # True
    print(f"is_value_valid_for_type('2023-10-27 15:30:00', 'datetime'): {is_value_valid_for_type('2023-10-27 15:30:00', 'datetime')}") # True
    print(f"is_value_valid_for_type('true', 'boolean'): {is_value_valid_for_type('true', 'boolean')}") # True
    print(f"is_value_valid_for_type(1, 'boolean'): {is_value_valid_for_type(1, 'boolean')}")       # True
    print(f"is_value_valid_for_type(None, 'integer'): {is_value_valid_for_type(None, 'integer')}") # True
    print(f"is_value_valid_for_type('text', 'unknown'): {is_value_valid_for_type('text', 'unknown')}") # False