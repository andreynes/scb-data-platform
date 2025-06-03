# etl/src/extract/mongo_extractor.py
from typing import Optional, Dict, Any, Union, IO, List
from pymongo import MongoClient
from pymongo.database import Database
from bson import ObjectId # Для преобразования строкового ID в ObjectId, если нужно
from gridfs import GridFS # Если будете хранить файлы в GridFS

# Настройки подключения (могут быть вынесены в config_utils.py или передаваться)
# Для примера, если не используется централизованная конфигурация
# MONGO_DB_URL = "mongodb://localhost:27017/" 
# MONGO_DB_NAME = "scb_db_data_lake"
# RAW_DATA_LAKE_COLLECTION = "raw_data_lake"

def get_document_metadata(
    document_id: str,
    mongo_db: Database, # Передаем объект базы данных
    raw_data_lake_collection_name: str = "raw_data_lake" # Имя коллекции по умолчанию
) -> Optional[Dict[str, Any]]:
    """
    Извлекает полный документ метаданных из MongoDB по его ID.

    Args:
        document_id: Уникальный идентификатор документа (обычно строка).
        mongo_db: Экземпляр pymongo.database.Database для подключения к MongoDB.
        raw_data_lake_collection_name: Название коллекции, где хранятся метаданные.

    Returns:
        Словарь с метаданными документа или None, если документ не найден.
    """
    collection = mongo_db[raw_data_lake_collection_name]
    try:
        # Попытка найти по ObjectId, если document_id - это валидный ObjectId_str
        # Это более надежно, если _id у вас ObjectId
        metadata_doc = collection.find_one({"_id": ObjectId(document_id)})
    except Exception: # bson.errors.InvalidId
        # Если не ObjectId, или ошибка преобразования, пробуем как строку (если у вас document_id строковый)
        metadata_doc = collection.find_one({"document_id": document_id}) 
        if not metadata_doc: # И на всякий случай, если _id тоже может быть строкой
             metadata_doc = collection.find_one({"_id": document_id})

    if metadata_doc:
        # Преобразуем ObjectId в строку для JSON-совместимости, если нужно
        if '_id' in metadata_doc and isinstance(metadata_doc['_id'], ObjectId):
            metadata_doc['_id'] = str(metadata_doc['_id'])
        return metadata_doc
    return None

def get_json_representation_from_metadata(
    metadata: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Извлекает поле 'json_representation' из документа метаданных.

    Args:
        metadata: Словарь метаданных документа.

    Returns:
        Словарь с JSON-представлением или None, если поле отсутствует.
    """
    return metadata.get("json_representation")

def get_original_file_content_from_gridfs(
    file_ref_id: str, # Это _id файла в GridFS, сохраненный в метаданных
    mongo_db: Database # Передаем объект базы данных
) -> Optional[bytes]:
    """
    (Опционально) Извлекает содержимое оригинального файла из GridFS по его ID.
    Используется, если оригинальные файлы хранятся в GridFS.

    Args:
        file_ref_id: Строковый _id файла в GridFS.
        mongo_db: Экземпляр pymongo.database.Database.

    Returns:
        Содержимое файла в байтах или None, если файл не найден или ошибка.
    """
    fs = GridFS(mongo_db)
    try:
        grid_out = fs.get(ObjectId(file_ref_id)) # ID в GridFS обычно ObjectId
        return grid_out.read()
    except Exception as e: # gridfs.errors.NoFile и другие
        print(f"Error getting file from GridFS with id {file_ref_id}: {e}")
        return None

# --- Пример использования (для локального теста) ---
if __name__ == '__main__':
    # Эти настройки должны быть актуальными для вашего локального MongoDB
    TEST_MONGO_DB_URL = "mongodb://localhost:27017/"
    TEST_MONGO_DB_NAME = "scb_db_data_lake" # Убедитесь, что эта БД существует
    TEST_COLLECTION_NAME = "raw_data_lake" # Убедитесь, что эта коллекция существует

    client = None # Инициализируем client как None
    try:
        client = MongoClient(TEST_MONGO_DB_URL)
        db = client[TEST_MONGO_DB_NAME]
        print(f"Successfully connected to MongoDB: {TEST_MONGO_DB_URL}")

        # --- Предположим, у вас есть документ с таким _id или document_id ---
        # Замените на реальный ID из вашей базы для теста
        test_doc_id_str = "your_test_document_id_here" 

        # 1. Тест get_document_metadata
        print(f"\n--- Testing get_document_metadata for doc_id: {test_doc_id_str} ---")
        metadata = get_document_metadata(test_doc_id_str, db, TEST_COLLECTION_NAME)
        if metadata:
            print("Metadata found:")
            # print(metadata) # Раскомментируйте, чтобы увидеть все метаданные
            
            # 2. Тест get_json_representation_from_metadata
            print(f"\n--- Testing get_json_representation_from_metadata ---")
            json_repr = get_json_representation_from_metadata(metadata)
            if json_repr:
                print("JSON representation found:")
                # print(json_repr) # Раскомментируйте, чтобы увидеть JSON
            else:
                print("JSON representation NOT found in metadata.")

            # 3. Тест get_original_file_content_from_gridfs (если используется)
            #    Предполагается, что в метаданных есть поле 'original_file_ref_gridfs_id'
            #    и оно содержит ObjectId файла в GridFS
            gridfs_file_id_str = metadata.get("original_file_ref_gridfs_id") # Пример имени поля
            if gridfs_file_id_str:
                print(f"\n--- Testing get_original_file_content_from_gridfs for file_id: {gridfs_file_id_str} ---")
                file_content = get_original_file_content_from_gridfs(gridfs_file_id_str, db)
                if file_content:
                    print(f"File content retrieved from GridFS (first 100 bytes): {file_content[:100]}...")
                else:
                    print("File content NOT found in GridFS or error retrieving.")
            else:
                print("\nNo GridFS file reference found in metadata (field 'original_file_ref_gridfs_id'). Skipping GridFS test.")
        else:
            print(f"Metadata NOT found for document_id: {test_doc_id_str}")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        if client:
            client.close()
            print("\nMongoDB connection closed.")