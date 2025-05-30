# backend/app/repositories/data_lake_repo.py
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket # Если используем GridFS
from bson import ObjectId # Для работы с GridFS ID и _id MongoDB
from bson.errors import InvalidId
import logging

logger = logging.getLogger(__name__)

# Предполагаем, что имя коллекции метаданных определено где-то, например, в конфиге или как константа
RAW_DATA_LAKE_COLLECTION = "raw_data_lake" 
# RAW_FILES_GRIDFS_BUCKET = "raw_files" # Имя бакета для GridFS

class DataLakeRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[RAW_DATA_LAKE_COLLECTION]
        # Если используем GridFS через репозиторий:
        # self.fs = AsyncIOMotorGridFSBucket(db, bucket_name=RAW_FILES_GRIDFS_BUCKET)

    async def save_file_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Сохраняет метаданные файла в коллекцию.
        Ожидается, что metadata уже содержит _id (или document_id),
        либо MongoDB сгенерирует его.
        Возвращает ID созданного документа.
        """
        # Если _id генерируется здесь, а не передается в metadata:
        # if "_id" not in metadata and "document_id" not in metadata:
        #     metadata["_id"] = ObjectId() # или str(uuid.uuid4())
        # elif "document_id" in metadata and "_id" not in metadata:
        #      metadata["_id"] = metadata["document_id"] # Если используем document_id как _id

        result = await self.collection.insert_one(metadata)
        logger.info(f"Saved metadata for document_id: {result.inserted_id}")
        return str(result.inserted_id)

    # --- Опционально: Методы для прямого сохранения файла в GridFS через репозиторий ---
    # Если вы решите сохранять файлы напрямую из сервиса, эти методы могут быть не нужны здесь.
    # async def save_original_file_gridfs(self, filename: str, file_content: bytes, 
    #                                    document_id: str, content_type: Optional[str] = None) -> str:
    #     """
    #     Сохраняет содержимое файла в GridFS.
    #     Возвращает ID файла из GridFS (ObjectId, преобразованный в строку).
    #     """
    #     try:
    #         file_id = await self.fs.upload_from_stream(
    #             filename,
    #             file_content, # motor ожидает file-like object, BytesIO(file_content) если file_content это bytes
    #             metadata={"document_id": document_id, "contentType": content_type}
    #         )
    #         logger.info(f"Saved file to GridFS with ID: {file_id} for document_id: {document_id}")
    #         return str(file_id)
    #     except Exception as e:
    #         logger.error(f"Error saving file to GridFS for document_id {document_id}: {e}")
    #         raise

    # async def get_original_file_gridfs(self, gridfs_file_id: str) -> Optional[bytes]:
    #     """
    #     Извлекает содержимое файла из GridFS по его ID.
    #     """
    #     try:
    #         gridfs_id_obj = ObjectId(gridfs_file_id)
    #         grid_out = await self.fs.open_download_stream(gridfs_id_obj)
    #         file_content = await grid_out.read()
    #         return file_content
    #     except InvalidId:
    #         logger.error(f"Invalid GridFS ID format: {gridfs_file_id}")
    #         return None
    #     except Exception as e: # Например, NoFile если файл не найден
    #         logger.error(f"Error reading file from GridFS ID {gridfs_file_id}: {e}")
    #         return None
    # ------------------------------------------------------------------------------------

    async def get_file_metadata_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает метаданные файла по его document_id (или _id).
        """
        try:
            # Пытаемся сначала как ObjectId, если document_id может быть им
            oid = ObjectId(document_id)
            doc = await self.collection.find_one({"_id": oid})
        except InvalidId:
            # Если не ObjectId, ищем по строковому document_id (если у вас есть такое поле)
            # или предполагаем, что document_id это уже строковый _id
            doc = await self.collection.find_one({"document_id": document_id})
            if not doc: # Если нет поля document_id, ищем по _id как строке (если вы так храните)
                doc = await self.collection.find_one({"_id": document_id})

        if doc:
            # Преобразуем ObjectId в строку для консистентности, если нужно
            if isinstance(doc.get("_id"), ObjectId):
                doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_json_representation_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Извлекает только поле json_representation из документа метаданных.
        """
        metadata = await self.get_file_metadata_by_id(document_id)
        if metadata:
            return metadata.get("json_representation")
        return None

    async def update_processing_status(
        self, 
        document_id: str, 
        status: str, 
        error_message: Optional[str] = None,
        processing_details: Optional[Dict[str, Any]] = None # Для доп. инфо об обработке
    ) -> bool:
        """
        Обновляет статус обработки и сообщение об ошибке для документа.
        Возвращает True если документ найден и обновлен, иначе False.
        """
        update_fields: Dict[str, Any] = {"processing_status": status}
        if error_message is not None:
            update_fields["error_message"] = error_message
        else:
            # Если статус не Error, имеет смысл очищать предыдущее сообщение об ошибке
            if status != "Error": # Пример
                update_fields["$unset"] = {"error_message": ""} 
        
        if processing_details is not None:
            update_fields["processing_details"] = processing_details # или $set: {"processing_details.field": value}

        # Добавляем временную метку последнего обновления статуса
        from datetime import datetime, timezone
        update_fields["last_status_update_at"] = datetime.now(timezone.utc)

        try:
            # Определяем, по какому полю искать: _id или document_id
            # Для простоты будем считать, что document_id это и есть _id или уникальный индексированный ключ
            filter_query: Dict[str, Any]
            try:
                oid = ObjectId(document_id)
                filter_query = {"_id": oid}
            except InvalidId:
                filter_query = {"document_id": document_id} 
                # Если вы используете строковый UUID как _id, то можно сразу:
                # filter_query = {"_id": document_id}

            update_operation: Dict[str, Any] = {}
            if "$unset" in update_fields:
                update_operation["$unset"] = update_fields.pop("$unset")
            if update_fields: # Если остались поля для $set
                 update_operation["$set"] = update_fields

            if not update_operation: # Если ничего не обновляется (маловероятно)
                return True 

            result = await self.collection.update_one(filter_query, update_operation)
            
            if result.matched_count > 0:
                logger.info(f"Updated status for document_id: {document_id} to {status}")
                return True
            else:
                logger.warning(f"Document not found for status update, document_id: {document_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating status for document_id {document_id}: {e}")
            raise # Или return False, в зависимости от желаемого поведения

    # --- Существующие методы из вашего плана (если они уже есть) ---
    # async def get_files_for_verification(...)
    # async def delete_file_and_metadata(...)