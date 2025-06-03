# etl/src/load/mongo_updater.py
from typing import Dict, Any, Optional
from pymongo.database import Database
from pymongo.results import UpdateResult
from datetime import datetime, timezone # Используем timezone-aware datetime
from ...utils.logging_utils import setup_etl_logger # Наш логгер

logger = setup_etl_logger(__name__)

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

    Args:
        mongo_db: Экземпляр pymongo.database.Database.
        document_id: ID документа (обычно _id или document_id в коллекции метаданных).
        status: Новый статус обработки документа.
        error_message: Сообщение об ошибке, если статус - ошибка.
        processing_details: Дополнительные детали процесса обработки.
        raw_data_lake_collection_name: Имя коллекции метаданных.

    Returns:
        True, если документ был найден и обновлен, иначе False.
    """
    collection = mongo_db[raw_data_lake_collection_name]
    
    update_payload = {
        "processing_status": status,
        "last_processed_timestamp": datetime.now(timezone.utc) # Важно использовать UTC
    }

    if error_message:
        update_payload["error_message"] = error_message
    else:
        # Если статус не ошибка, можно очистить предыдущее сообщение об ошибке
        # update_payload["error_message"] = None # Или использовать $unset
        pass # Для простоты пока оставим как есть, если нет новой ошибки

    if processing_details:
        update_payload["processing_details"] = processing_details
    
    logger.info(f"Updating status for doc_id '{document_id}' to '{status}' in collection '{raw_data_lake_collection_name}'.")
    
    try:
        # Пытаемся найти по _id как ObjectId сначала, если document_id может быть таким
        from bson import ObjectId, errors as bson_errors
        try:
            obj_id = ObjectId(document_id)
            filter_query = {"_id": obj_id}
        except bson_errors.InvalidId:
            # Если не ObjectId, используем как строку для поля document_id или _id
            filter_query = {"document_id": document_id} 
            # Если у вас ID всегда в _id и он строковый, то: filter_query = {"_id": document_id}
    except ImportError: # Если bson не установлен или не используется ObjectId
         filter_query = {"document_id": document_id} # Или {"_id": document_id}

    update_result: UpdateResult = collection.update_one(
        filter_query,
        {"$set": update_payload}
    )

    if update_result.matched_count > 0:
        if update_result.modified_count > 0:
            logger.info(f"Successfully updated status for doc_id '{document_id}'.")
        else:
            logger.info(f"Document '{document_id}' found, but status was already '{status}' (or no changes made).")
        return True
    else:
        logger.warning(f"Document with id '{document_id}' not found for status update.")
        return False
except Exception as e:
    logger.error(f"Error updating document status for doc_id '{document_id}': {e}")
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