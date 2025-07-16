# etl/src/load/clickhouse_loader.py
from typing import List, Dict, Any, Optional, Tuple
from clickhouse_connect.driver import Client as ClickHouseClient # Или другой драйвер, если используется
from src.utils.logging_utils import setup_etl_logger

logger = setup_etl_logger(__name__)

# Для MVP предполагаем, что target_table и ее структура известны
# и соответствуют ontology_schema.
# Логика NULL_NOT_REPARSED будет добавлена позже (или уже частично в validator.py)

def _prepare_batch_for_insert(
    data_batch: List[Dict[str, Any]],
    column_order: List[str] # Ожидаемый порядок колонок для INSERT
) -> List[Tuple[Any, ...]]:
    """
    Подготавливает пакет данных к вставке:
    - Преобразует список словарей в список кортежей.
    - Гарантирует правильный порядок значений в кортежах согласно column_order.
    - Обрабатывает отсутствующие ключи в словарях (вставляет None).
    """
    prepared_batch = []
    for row_dict in data_batch:
        row_tuple = []
        for col_name in column_order:
            row_tuple.append(row_dict.get(col_name)) # .get() вернет None, если ключ отсутствует
        prepared_batch.append(tuple(row_tuple))
    return prepared_batch

def load_data_to_warehouse(
    data_to_load: List[Dict[str, Any]],
    ch_client: ClickHouseClient,
    target_table: str, # Полное имя таблицы, например, 'scb_warehouse.atomic_data_warehouse'
    ontology_schema: Dict[str, Any], # Для определения порядка колонок и, возможно, типов
    original_document_id: str, # Для логирования и, возможно, как поле в таблице
    ontology_version: str, # Для логирования и, возможно, как поле в таблице
    batch_size: int = 10000
) -> bool:
    """
    Загружает обработанные данные в ClickHouse.

    Args:
        data_to_load: Список словарей с данными для загрузки.
        ch_client: Активный клиент ClickHouse.
        target_table: Имя целевой таблицы.
        ontology_schema: Схема онтологии (для определения колонок и их порядка).
        original_document_id: ID исходного документа.
        ontology_version: Версия онтологии, по которой данные были обработаны.
        batch_size: Размер пакета для вставки.

    Returns:
        True в случае успеха, False в случае ошибки.
    """
    if not data_to_load:
        logger.info(f"No data to load for document_id: {original_document_id}.")
        return True # Считаем успехом, если нечего загружать

    # Определяем порядок и имена колонок из онтологии
    # Добавляем системные поля, если они есть в таблице ClickHouse
    # и не приходят с data_to_load
    # Для MVP предполагаем, что data_to_load уже содержит все нужные поля,
    # включая original_document_id и ontology_version, если они есть в таблице.
    # Или что их нужно добавить сейчас.
    
    # Получаем список имен атрибутов из онтологии в правильном порядке
    # Это важно, чтобы данные вставлялись в правильные колонки
    # Если таблица ClickHouse имеет строго определенный порядок, он должен быть здесь
    try:
        # Для MVP порядок может быть просто по алфавиту или как в онтологии
        column_names = [attr['name'] for attr in ontology_schema.get('attributes', [])]
        
        # Добавляем системные поля, если они должны быть в каждой строке
        # и их нет в data_to_load (или их нужно перезаписать)
        # Пример:
        # if 'original_document_id' not in column_names: column_names.append('original_document_id')
        # if 'ontology_version' not in column_names: column_names.append('ontology_version')
        # if 'load_timestamp' not in column_names: column_names.append('load_timestamp') # если генерируем здесь

    except Exception as e:
        logger.error(f"Error determining column order from ontology for doc_id {original_document_id}: {e}")
        return False

    if not column_names:
        logger.error(f"Could not determine column names from ontology for doc_id {original_document_id}.")
        return False

    logger.info(f"Loading {len(data_to_load)} rows for doc_id {original_document_id} into {target_table} with columns: {column_names}")

    try:
        # Добавляем системные поля к каждой строке данных, если нужно
        enriched_data_to_load = []
        for row in data_to_load:
            new_row = row.copy() # Работаем с копией
            if 'original_document_id' not in new_row: # Пример добавления
                new_row['original_document_id'] = original_document_id
            if 'ontology_version' not in new_row: # Пример добавления
                new_row['ontology_version'] = ontology_version
            # if 'load_timestamp' not in new_row:
            #    from datetime import datetime
            #    new_row['load_timestamp'] = datetime.utcnow()
            enriched_data_to_load.append(new_row)
        
        data_to_load = enriched_data_to_load

        # Пакетная вставка
        for i in range(0, len(data_to_load), batch_size):
            batch = data_to_load[i:i + batch_size]
            prepared_batch = _prepare_batch_for_insert(batch, column_names)
            
            logger.debug(f"Inserting batch {i // batch_size + 1} of size {len(batch)} for doc_id {original_document_id}")
            ch_client.insert(
                table=target_table,
                data=prepared_batch,
                column_names=column_names
            )
        logger.info(f"Successfully loaded {len(data_to_load)} rows for doc_id {original_document_id} into {target_table}.")
        return True
    except Exception as e:
        logger.error(f"Error loading data to ClickHouse for doc_id {original_document_id}: {e}")
        # Здесь можно добавить более детальное логирование, например, какие данные вызвали ошибку
        return False

if __name__ == '__main__':
    # Для локального теста нужен запущенный ClickHouse и клиент
    # from clickhouse_connect import get_client
    # ch_test_client = get_client(host='localhost', user='default', password='')
    # ch_test_client.command('CREATE DATABASE IF NOT EXISTS scb_warehouse')
    
    # Пример таблицы (упрощенный, без ReplacingMergeTree для простоты теста)
    # CREATE TABLE IF NOT EXISTS scb_warehouse.atomic_data_warehouse (
    #    original_document_id String,
    #    ontology_version String,
    #    product_name Nullable(String),
    #    price_rub Nullable(Float64)
    # ) ENGINE = MergeTree() ORDER BY original_document_id;

    test_data = [
        {"product_name": "Молоко", "price_rub": 123.45}, # original_document_id и ontology_version добавятся
        {"product_name": "Хлеб", "price_rub": None}
    ]
    test_ontology = {
        "attributes": [
            {"name": "product_name", "type": "string"},
            {"name": "price_rub", "type": "float"},
            {"name": "original_document_id", "type": "string"}, # Добавим их в онтологию, чтобы они были в column_names
            {"name": "ontology_version", "type": "string"}
        ]
    }
    doc_id = "test_doc_ch_loader"
    ont_version = "v1.0"
    target = "scb_warehouse.atomic_data_warehouse"

    # print(f"--- Testing load_data_to_warehouse ---")
    # success = load_data_to_warehouse(test_data, ch_test_client, target, test_ontology, doc_id, ont_version)
    # print(f"Load successful: {success}")
    # Если успешно, можно проверить данные в ClickHouse
    # print(ch_test_client.query(f"SELECT * FROM {target} WHERE original_document_id = '{doc_id}'").result_rows)
    # ch_test_client.command(f"ALTER TABLE {target} DELETE WHERE original_document_id = '{doc_id}'") # Очистка
    pass # Раскомментируйте для теста с реальным ClickHouse