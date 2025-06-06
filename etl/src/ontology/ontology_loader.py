# path/to/your/project/etl/src/ontology/ontology_loader.py

from typing import Optional, Dict, List, Any
# Предполагается, что вы будете использовать Pymongo или Motor для работы с MongoDB
# Пример с Pymongo (синхронный, более вероятен для стандартных PythonOperator в Airflow)
# Если используете Motor (асинхронный), импорты и вызовы будут другими.
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

logger = logging.getLogger(__name__)

# Имена коллекций могут быть вынесены в конфигурацию или передаваться как параметры
# Для простоты MVP, можно захардкодить или использовать значения по умолчанию
DEFAULT_STATUS_COLLECTION_NAME = "ontology_status"
DEFAULT_SCHEMA_COLLECTION_NAME = "ontology_schemas"
DEFAULT_VOCAB_COLLECTION_NAME = "ontology_vocabularies"
ACTIVE_CONFIG_DOC_ID = "active_config" # ID документа, хранящего активную версию


def _get_active_ontology_version_id(
    db: Database,
    collection_names: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Приватная функция для получения ID текущей активной версии онтологии.
    """
    coll_names = collection_names or {}
    status_collection_name = coll_names.get('status', DEFAULT_STATUS_COLLECTION_NAME)
    try:
        status_collection = db[status_collection_name]
        active_config_doc = status_collection.find_one({"_id": ACTIVE_CONFIG_DOC_ID})
        if active_config_doc and "active_version" in active_config_doc:
            version_id = active_config_doc["active_version"]
            logger.info(f"Active ontology version ID: {version_id}")
            return str(version_id)
        else:
            logger.warning(f"Document with _id '{ACTIVE_CONFIG_DOC_ID}' or field 'active_version' not found in '{status_collection_name}'.")
            return None
    except (ConnectionFailure, OperationFailure) as e:
        logger.error(f"MongoDB error while fetching active ontology version: {e}")
        # В реальном ETL, возможно, стоит пробрасывать исключение или возвращать маркер ошибки
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching active ontology version: {e}")
        return None


def get_current_ontology_schema(
    db: Database,
    collection_names: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Загружает полную структуру (схему) текущей активной версии онтологии из MongoDB.
    """
    active_version_id = _get_active_ontology_version_id(db, collection_names)
    if not active_version_id:
        return None

    coll_names = collection_names or {}
    schema_collection_name = coll_names.get('schemas', DEFAULT_SCHEMA_COLLECTION_NAME)
    try:
        schema_collection = db[schema_collection_name]
        # В MongoDB _id часто является ObjectId, но если вы сохраняете version_id как строку
        # и используете ее как _id, то ObjectId не нужен.
        # Если version_id должен быть ObjectId, нужно будет импортировать `from bson import ObjectId`
        # и использовать `ObjectId(active_version_id)`
        schema_doc = schema_collection.find_one({"_id": active_version_id}) # или {"version": active_version_id}
        if schema_doc:
            logger.info(f"Successfully loaded ontology schema for version: {active_version_id}")
            # Убираем _id из документа перед возвратом, если он не часть самой схемы
            schema_doc.pop("_id", None)
            return schema_doc
        else:
            logger.warning(f"Ontology schema for version '{active_version_id}' not found in '{schema_collection_name}'.")
            return None
    except (ConnectionFailure, OperationFailure) as e:
        logger.error(f"MongoDB error while fetching ontology schema version {active_version_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching ontology schema version {active_version_id}: {e}")
        return None


def get_ontology_vocabulary(
    vocabulary_name: str,
    db: Database,
    active_version_id: Optional[str] = None, # Может быть передан для оптимизации
    collection_names: Optional[Dict[str, str]] = None
) -> Optional[List[Any]]:
    """
    Загружает список допустимых значений для указанного справочника
    текущей активной версии онтологии.
    """
    if not active_version_id:
        active_version_id = _get_active_ontology_version_id(db, collection_names)
    if not active_version_id:
        return None

    coll_names = collection_names or {}
    vocab_collection_name = coll_names.get('vocabularies', DEFAULT_VOCAB_COLLECTION_NAME)
    try:
        vocab_collection = db[vocab_collection_name]
        # Предполагаем, что справочники хранятся как документы с полями 'name', 'version', 'values'
        vocab_doc = vocab_collection.find_one({
            "name": vocabulary_name,
            "version": active_version_id
        })
        if vocab_doc and "values" in vocab_doc:
            logger.info(f"Successfully loaded vocabulary '{vocabulary_name}' for version: {active_version_id}")
            return vocab_doc["values"]
        else:
            logger.warning(f"Vocabulary '{vocabulary_name}' for version '{active_version_id}' not found or 'values' field missing in '{vocab_collection_name}'.")
            return None
    except (ConnectionFailure, OperationFailure) as e:
        logger.error(f"MongoDB error while fetching vocabulary {vocabulary_name} (version {active_version_id}): {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching vocabulary {vocabulary_name} (version {active_version_id}): {e}")
        return None

def get_multiple_vocabularies(
    vocabulary_names: List[str],
    db: Database,
    active_version_id: Optional[str] = None,
    collection_names: Optional[Dict[str, str]] = None
) -> Dict[str, List[Any]]:
    """
    Загружает несколько справочников для текущей активной версии онтологии.
    """
    if not active_version_id:
        active_version_id = _get_active_ontology_version_id(db, collection_names)
    if not active_version_id:
        return {}

    coll_names = collection_names or {}
    vocab_collection_name = coll_names.get('vocabularies', DEFAULT_VOCAB_COLLECTION_NAME)
    results: Dict[str, List[Any]] = {}
    try:
        vocab_collection = db[vocab_collection_name]
        # Используем $in для получения нескольких документов за один запрос
        query = {
            "name": {"$in": vocabulary_names},
            "version": active_version_id
        }
        for vocab_doc in vocab_collection.find(query):
            if vocab_doc and "name" in vocab_doc and "values" in vocab_doc:
                results[vocab_doc["name"]] = vocab_doc["values"]
        
        # Логируем, какие справочники не были найдены, если это необходимо
        for name in vocabulary_names:
            if name not in results:
                logger.warning(f"Vocabulary '{name}' for version '{active_version_id}' not found in '{vocab_collection_name}'.")
        
        logger.info(f"Loaded {len(results)} vocabularies for version: {active_version_id}")
        return results
    except (ConnectionFailure, OperationFailure) as e:
        logger.error(f"MongoDB error while fetching multiple vocabularies (version {active_version_id}): {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error fetching multiple vocabularies (version {active_version_id}): {e}")
        return {}

# Вы можете добавить сюда другие вспомогательные функции или классы,
# если они описаны в вашей документации для ontology_loader.py