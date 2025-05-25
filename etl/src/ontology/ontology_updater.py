from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Имена коллекций по умолчанию
DEFAULT_SCHEMA_COLLECTION_NAME = "ontology_schemas"
DEFAULT_VOCABULARY_COLLECTION_NAME = "ontology_vocabularies"
DEFAULT_STATUS_COLLECTION_NAME = "ontology_status"
ACTIVE_CONFIG_DOC_ID = "active_ontology_config" # ID документа, хранящего активную версию

def _get_mongo_client(mongo_uri: str) -> Optional[MongoClient]:
    """Подключается к MongoDB."""
    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping') # Проверка соединения
        logger.info("Successfully connected to MongoDB.")
        return client
    except ConnectionFailure:
        logger.error(f"Failed to connect to MongoDB at {mongo_uri}")
        return None

def _get_active_ontology_version_id(db_client: MongoClient, db_name: str, collection_names: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Получает ID текущей активной версии онтологии из MongoDB."""
    cols = collection_names or {}
    status_col_name = cols.get('status', DEFAULT_STATUS_COLLECTION_NAME)
    
    try:
        db = db_client[db_name]
        status_doc = db[status_col_name].find_one({"_id": ACTIVE_CONFIG_DOC_ID})
        if status_doc and "active_version" in status_doc:
            return str(status_doc["active_version"])
        logger.warning(f"Active ontology version config document ('{ACTIVE_CONFIG_DOC_ID}') or 'active_version' field not found in '{status_col_name}'.")
        return None
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed while fetching active version: {e}")
        return None


def upload_ontology_version(
    version_id: str,
    schema_data: Dict[str, Any],
    vocabularies_data: Dict[str, List[Any]],
    db_client: MongoClient,
    db_name: str,
    collection_names: Optional[Dict[str, str]] = None
) -> bool:
    """
    Загружает (или перезаписывает) определение схемы и справочников
    для указанной версии онтологии в MongoDB.
    Не делает эту версию активной.
    """
    cols = collection_names or {}
    schema_col_name = cols.get('schemas', DEFAULT_SCHEMA_COLLECTION_NAME)
    vocab_col_name = cols.get('vocabularies', DEFAULT_VOCABULARY_COLLECTION_NAME)
    
    try:
        db = db_client[db_name]
        
        # 1. Загрузка/Обновление схемы
        schema_doc = {"_id": version_id, "version": version_id, **schema_data}
        schema_doc['upload_timestamp_utc'] = datetime.now(timezone.utc)
        
        db[schema_col_name].replace_one(
            {"_id": version_id},
            schema_doc,
            upsert=True
        )
        logger.info(f"Schema for ontology version '{version_id}' uploaded/updated in '{schema_col_name}'.")

        # 2. Загрузка/Обновление справочников
        if vocabularies_data:
            operations = []
            for vocab_name, values_list in vocabularies_data.items():
                vocab_doc = {
                    "name": vocab_name,
                    "version": version_id,
                    "values": values_list,
                    "upload_timestamp_utc": datetime.now(timezone.utc)
                }
                operations.append(UpdateOne(
                    {"name": vocab_name, "version": version_id},
                    {"$set": vocab_doc},
                    upsert=True
                ))
            
            if operations:
                result = db[vocab_col_name].bulk_write(operations)
                logger.info(f"Uploaded/updated {result.upserted_count + result.modified_count} vocabularies for version '{version_id}' in '{vocab_col_name}'.")
        else:
            logger.info(f"No vocabularies data provided for version '{version_id}'.")
        
        return True
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed during ontology upload for version '{version_id}': {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during ontology upload for version '{version_id}': {e}")
        return False

def set_active_ontology_version(
    version_id: str,
    db_client: MongoClient,
    db_name: str,
    collection_names: Optional[Dict[str, str]] = None
) -> bool:
    """
    Атомарно устанавливает указанную версию онтологии как активную.
    """
    cols = collection_names or {}
    status_col_name = cols.get('status', DEFAULT_STATUS_COLLECTION_NAME)
    schema_col_name = cols.get('schemas', DEFAULT_SCHEMA_COLLECTION_NAME)

    try:
        db = db_client[db_name]

        # Проверяем, существует ли сама схема этой версии
        if not db[schema_col_name].find_one({"_id": version_id}):
            logger.error(f"Cannot set active version to '{version_id}': schema for this version not found in '{schema_col_name}'.")
            return False

        update_result = db[status_col_name].update_one(
            {"_id": ACTIVE_CONFIG_DOC_ID},
            {"$set": {"active_version": version_id, "last_activated_utc": datetime.now(timezone.utc)}},
            upsert=True
        )
        
        if update_result.acknowledged and (update_result.modified_count > 0 or update_result.upserted_id is not None):
            logger.info(f"Successfully set active ontology version to '{version_id}'.")
            return True
        else:
            logger.error(f"Failed to set active ontology version to '{version_id}' (update not acknowledged or no changes made).")
            return False
    except OperationFailure as e:
        logger.error(f"MongoDB operation failed while setting active version to '{version_id}': {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while setting active version to '{version_id}': {e}")
        return False

# Пример использования (для локального тестирования)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # --- Используем ваши учетные данные ---
    # Эти значения взяты из вашего infra/compose/.env
    MONGO_USER_FROM_ENV = "andrewkrylov"
    MONGO_PASSWORD_FROM_ENV = "12345dbscb"
    TEST_MONGO_URI = "mongodb://andrewkrylov:12345dbscb@localhost:27017/?authSource=admin"
    
    TEST_DB_NAME = "scb_ontology_updater_local_test" # Выберите имя для тестовой БД
    # ---------------------------------------------------------------

    client = _get_mongo_client(TEST_MONGO_URI)
    if not client:
        logger.error("Exiting due to MongoDB connection failure.")
        exit(1) # Выход, если подключение не удалось
    
    # Для чистоты теста, можно удалить тестовые коллекции перед запуском
    # Будьте ОЧЕНЬ ОСТОРОЖНЫ, если TEST_DB_NAME - это не тестовая база!
    logger.warning(f"About to drop collections in {TEST_DB_NAME} if they exist...")
    logger.warning("Collections to be dropped:")
    logger.warning(f"  - {client[TEST_DB_NAME][DEFAULT_SCHEMA_COLLECTION_NAME].name}")
    logger.warning(f"  - {client[TEST_DB_NAME][DEFAULT_VOCABULARY_COLLECTION_NAME].name}")
    logger.warning(f"  - {client[TEST_DB_NAME][DEFAULT_STATUS_COLLECTION_NAME].name}")
    # client[TEST_DB_NAME][DEFAULT_SCHEMA_COLLECTION_NAME].drop()
    # client[TEST_DB_NAME][DEFAULT_VOCABULARY_COLLECTION_NAME].drop()
    # client[TEST_DB_NAME][DEFAULT_STATUS_COLLECTION_NAME].drop()
    # logger.info("Old test collections (if any) dropped. (Actually commented out, uncomment to enable)")


    test_version_id_1 = "v0.9-test"
    test_schema_1 = {"version": test_version_id_1, "description": "Test Schema v0.9", "attributes": [{"name": "attr1", "type": "string"}]}
    test_vocabs_1 = {"countries_test": ["TestCountry1", "TestCountry2"]}

    logger.info(f"\n--- Testing upload_ontology_version for {test_version_id_1} ---")
    success_upload_1 = upload_ontology_version(test_version_id_1, test_schema_1, test_vocabs_1, client, TEST_DB_NAME)
    logger.info(f"Upload success for {test_version_id_1}: {success_upload_1}")

    test_version_id_2 = "v1.0-test"
    test_schema_2 = {"version": test_version_id_2, "description": "Test Schema v1.0", "attributes": [{"name": "test_attr_v1", "type": "integer"}]}
    test_vocabs_2 = {"countries_test": ["CountryA", "CountryB"], "periods_test": ["Year", "Month"]}
    
    logger.info(f"\n--- Testing upload_ontology_version for {test_version_id_2} ---")
    success_upload_2 = upload_ontology_version(test_version_id_2, test_schema_2, test_vocabs_2, client, TEST_DB_NAME)
    logger.info(f"Upload success for {test_version_id_2}: {success_upload_2}")

    logger.info(f"\n--- Testing set_active_ontology_version for {test_version_id_2} ---")
    success_set_active = set_active_ontology_version(test_version_id_2, client, TEST_DB_NAME)
    logger.info(f"Set active success for {test_version_id_2}: {success_set_active}")

    logger.info(f"\n--- Testing _get_active_ontology_version_id ---")
    active_id = _get_active_ontology_version_id(client, TEST_DB_NAME)
    logger.info(f"Current active version ID: {active_id}")
    
    if active_id == test_version_id_2:
        logger.info("Test PASSED: Active version is correctly set and retrieved.")
    else:
        logger.error(f"Test FAILED: Expected active version '{test_version_id_2}', but got '{active_id}'.")

    # Тест установки несуществующей версии как активной
    logger.info(f"\n--- Testing set_active_ontology_version for non-existent version 'v-non-existent' ---")
    success_set_non_existent = set_active_ontology_version("v-non-existent", client, TEST_DB_NAME)
    if not success_set_non_existent:
        logger.info("Test PASSED: Correctly failed to set non-existent version as active.")
    else:
        logger.error("Test FAILED: Incorrectly succeeded in setting non-existent version as active.")

    client.close()
    logger.info("MongoDB client closed.")