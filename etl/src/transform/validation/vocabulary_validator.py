# etl/src/transform/validation/vocabulary_validator.py
from typing import Any, List, Optional

def is_value_in_vocabulary(
    value: Any, 
    vocabulary_list: Optional[List[Any]],
    case_sensitive: bool = False # По умолчанию регистронезависимое сравнение для строк
) -> bool:
    """
    Проверяет, присутствует ли значение в списке допустимых значений (справочнике).
    None считается валидным, если его нет в справочнике (для обязательных полей проверка будет на другом этапе).
    """
    if vocabulary_list is None: # Если справочник не предоставлен, считаем валидным (или это ошибка?)
        # logger.warning(f"Vocabulary list not provided for value: {value}. Skipping vocabulary validation.")
        return True 
    
    if value is None: # Если значение None, а справочник есть, то это несовпадение
        return False # Или True, если None разрешен и его нет в справочнике? Зависит от бизнес-логики.
                     # Пока считаем, что если проверяем по справочнику, то значение должно быть из него.

    # Приводим значение и элементы справочника к строке для сравнения, если не case_sensitive
    str_value = str(value)
    
    for vocab_item in vocabulary_list:
        str_vocab_item = str(vocab_item)
        if case_sensitive:
            if str_value == str_vocab_item:
                return True
        else:
            if str_value.lower() == str_vocab_item.lower():
                return True
    return False

if __name__ == '__main__':
    countries = ['Россия', 'США', 'Китай']
    print(f"is_value_in_vocabulary('Россия', countries): {is_value_in_vocabulary('Россия', countries)}") # True
    print(f"is_value_in_vocabulary('сша', countries): {is_value_in_vocabulary('сша', countries)}")          # True
    print(f"is_value_in_vocabulary(' США ', countries): {is_value_in_vocabulary(' США '.strip(), countries)}") # True (если value предварительно очищено)
    print(f"is_value_in_vocabulary('Индия', countries): {is_value_in_vocabulary('Индия', countries)}")    # False
    print(f"is_value_in_vocabulary(None, countries): {is_value_in_vocabulary(None, countries)}")          # False (по текущей логике)
    print(f"is_value_in_vocabulary('Россия', None): {is_value_in_vocabulary('Россия', None)}")          # True (справочник не задан)
    
    numbers = [1, 2, 10]
    print(f"is_value_in_vocabulary(10, numbers): {is_value_in_vocabulary(10, numbers)}") # True
    print(f"is_value_in_vocabulary('10', numbers): {is_value_in_vocabulary('10', numbers)}") # True
    print(f"is_value_in_vocabulary(5, numbers): {is_value_in_vocabulary(5, numbers)}")   # False