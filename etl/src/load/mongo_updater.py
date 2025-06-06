# etl/src/load/mongo_updater.py
from typing import Dict, Any, Optional
from pymongo.database import Database
from pymongo.results import UpdateResult
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime, timezone 
import logging

logger = logging.getLogger(__name__)

def update_document_processing_status(
    mongo_db: Database,
    document_id: str,
    status: str, # Например, 'Processed', 'Error_Parsing', 'Error_Loading'
    error_message: Optional[str] = None,
    processing_details: Optional[Dict[str, Any]] = None, # Например, кол-во обработанных строк, warnings
    raw_data_lake_collection_name: str = "raw_data_lake"
) -> bool:
    """
    Обновляет статус обработки документа и связанные метаданные в MongoDB.
    # ... (остальная часть docstring) ...
    """
    collection = mongo_db[raw_data_lake_collection_name]
    
    update_payload = {
        "processing_status": status,
        "last_processed_timestamp": datetime.now(timezone.utc) # Важно использовать UTC
    }

    if error_message:
        update_payload["error_message"] = error_message
    else:
        # Если статус не ошибка, и поле error_message существует, его нужно очистить
        # Для этого используем $unset, если поле должно быть удалено,
        # или устанавливаем в null, если поле всегда присутствует.
        # Предположим, мы хотим его удалить, если ошибки нет.
        pass # $unset будет добавлен ниже, если нужно

    if processing_details:
        update_payload["processing_details"] = processing_details
    
    logger.info(f"Updating status for doc_id '{document_id}' to '{status}' in collection '{raw_data_lake_collection_name}'.")
    
    # Определение фильтра для поиска документа
    filter_query: Dict[str, Any]
    try:
        from bson import ObjectId, errors as bson_errors # Импорт внутри, т.к. может не быть нужен всегда
        try:
            obj_id = ObjectId(document_id)
            filter_query = {"_id": obj_id}
        except bson_errors.InvalidId:
            # Если document_id не является валидным ObjectId, ищем по другому полю
            # или предполагаем, что _id может быть строкой
            # Это зависит от того, как у вас хранятся ID.
            # Для примера, если document_id это альтернативный ключ:
            # filter_query = {"document_id_field": document_id}
            # Или если _id может быть строкой:
            filter_query = {"_id": document_id}
    except ImportError:
        # Если bson не доступен, предполагаем строковый ID
        filter_query = {"_id": document_id} # Или {"document_id_field": document_id}


    # Формируем операцию обновления, включая $unset для error_message если его нет
    update_operation: Dict[str, Any] = {"$set": update_payload}
    if not error_message and status != 'Error': # Пример условия для очистки ошибки
        update_operation["$unset"] = {"error_message": ""}


    try:
        update_result: UpdateResult = collection.update_one(
            filter_query,
            update_operation
        )

        if update_result.matched_count > 0:
            if update_result.modified_count > 0:
                logger.info(f"Successfully updated status for doc_id '{document_id}'.")
            else:
                logger.info(f"Document '{document_id}' found, but status was already '{status}' or no effective changes made to fields being set.")
            return True
        else:
            logger.warning(f"Document with query '{filter_query}' not found for status update in collection '{raw_data_lake_collection_name}'.")
            return False
            
    except (ConnectionFailure, OperationFailure) as db_op_error: # Более специфичные ошибки MongoDB
        logger.error(f"MongoDB operation error updating document status for doc_id '{document_id}': {db_op_error}")
        return False
    except Exception as e: # Общий обработчик других неожиданных ошибок
        logger.error(f"Unexpected error updating document status for doc_id '{document_id}': {e}", exc_info=True)
        return False

if __name__ == '__main__':
    # Для локального теста нужен запущенный MongoDB и клиент
    # from pymongo import MongoClient
    # TEST_MONGO_DB_URL = "mongodb://localhost:27017/"
    # TEST_MONGO_DB_NAME = "scb_db_data_lake"
    # client = MongoClient(TEST_MONGO_DB_URL)
    # test_db = client[TEST_MONGO_DB_NAME]

    # test_doc_id_to_update = "your_existing_document_id_for_test" 

    # print(f"--- Testing update_document_processing_status (Success) ---")
    # success = update_document_processing_status(
    #     test_db, test_doc_id_to_update, "Processed", 
    #     processing_details={"rows_loaded": 100, "warnings": 0}
    # )
    # print(f"Update 1 successful: {success}")

    # print(f"\n--- Testing update_document_processing_status (Error) ---")
    # error_success = update_document_processing_status(
    #     test_db, test_doc_id_to_update, "Error_Parsing", 
    #     error_message="Failed to parse Sheet1, unexpected format."
    # )
    # print(f"Update 2 successful (with error status): {error_success}")

    # print(f"\n--- Testing update_document_processing_status (Doc not found) ---")
    # not_found_success = update_document_processing_status(
    #     test_db, "non_existent_doc_id", "Processed"
    # )
    # print(f"Update 3 successful (doc not found): {not_found_success}") # Ожидаем False

    # client.close()
    pass # Раскомментируйте для теста с реальным MongoDB