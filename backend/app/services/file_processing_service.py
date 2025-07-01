# backend/app/services/file_processing_service.py
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import UploadFile

from repositories.data_lake_repo import DataLakeRepo
from schemas.file_schemas import FileUploadStatusSchema # Схема ответа
from schemas.user_schemas import UserSchema # Для информации о загрузившем
# from clients.airflow_client import AirflowClient # Если у вас есть отдельный Airflow клиент
# Для MVP можно использовать простой HTTP запрос к Airflow API или пока заглушку

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self, data_lake_repo: DataLakeRepo): #, airflow_client: Optional[AirflowClient] = None):
        self.data_lake_repo = data_lake_repo
        # self.airflow_client = airflow_client # Раскомментировать, когда будет клиент

    async def process_uploaded_files(
        self, files: List[UploadFile], uploader: UserSchema
    ) -> List[FileUploadStatusSchema]:
        """
        Обрабатывает список загруженных файлов: сохраняет их и инициирует ETL.
        """
        upload_statuses: List[FileUploadStatusSchema] = []

        for file in files:
            document_id = str(uuid.uuid4())
            original_filename = file.filename or "unknown_file"
            content_type = file.content_type or "application/octet-stream"
            
            logger.info(f"Processing file: {original_filename} for user: {uploader.username}, assigned document_id: {document_id}")

            try:
                # Шаг 1: (Опционально) Сохранить оригинальный файл, если это не делает data_lake_repo
                # Например, если data_lake_repo.save_file_metadata ожидает ссылку на уже сохраненный файл.
                # Для MVP, если файлы небольшие и хранятся в метаданных как JSON или ссылка на GridFS,
                # то содержимое файла может быть передано в data_lake_repo.
                # file_content = await file.read() # Читаем содержимое файла
                # gridfs_file_id = await self.data_lake_repo.save_original_file_gridfs(
                #    filename=original_filename, 
                #    file_content=file_content, 
                #    document_id=document_id,
                #    content_type=content_type
                # )
                # original_file_ref = f"gridfs://{gridfs_file_id}" # Пример ссылки

                # Шаг 2: Создать и сохранить метаданные
                metadata = {
                    # "_id": document_id, # Если используете document_id как _id в MongoDB
                    "document_id": document_id, # Или как отдельное поле
                    "original_filename": original_filename,
                    "content_type": content_type,
                    "size_bytes": file.size if file.size is not None else -1, # Размер файла, если доступен
                    "uploader_id": uploader.id, # ID пользователя из UserSchema
                    "uploader_username": uploader.username,
                    "upload_timestamp": datetime.now(timezone.utc),
                    "processing_status": "Accepted", # Начальный статус
                    # "original_file_ref": original_file_ref, # Если файл сохранен отдельно
                    "error_message": None,
                    "json_representation": None, # Будет заполнено на ранних этапах ETL
                }
                await self.data_lake_repo.save_file_metadata(metadata)

                # Шаг 3: Инициировать Airflow DAG
                # TODO: Реализовать вызов Airflow DAG. Пока заглушка.
                # if self.airflow_client:
                #     await self.airflow_client.trigger_dag(
                #         dag_id="file_processing_dag", # Убедитесь, что имя DAG совпадает
                #         conf={"document_id": document_id}
                #     )
                #     logger.info(f"Triggered Airflow DAG 'file_processing_dag' for document_id: {document_id}")
                # else:
                #     logger.warning("Airflow client not configured. Skipping DAG trigger.")
                
                # Пока просто логируем для MVP
                logger.info(f"Placeholder: Airflow DAG 'file_processing_dag' would be triggered for document_id: {document_id}")


                upload_statuses.append(
                    FileUploadStatusSchema(
                        filename=original_filename,
                        document_id=document_id,
                        status="Accepted"
                    )
                )

            except Exception as e:
                logger.error(f"Error processing file {original_filename} (doc_id: {document_id}): {e}", exc_info=True)
                # Попытка обновить статус в БД на Error, если метаданные уже были созданы
                try:
                    await self.data_lake_repo.update_processing_status(
                        document_id=document_id, 
                        status="Error_Upload", 
                        error_message=f"Initial processing failed: {str(e)}"
                    )
                except Exception as db_e:
                    logger.error(f"Failed to update status to Error_Upload for doc_id {document_id}: {db_e}")
                
                upload_statuses.append(
                    FileUploadStatusSchema(
                        filename=original_filename,
                        document_id=document_id, # Возвращаем ID, даже если была ошибка, для отслеживания
                        status="Error_Upload",
                        error_message=f"Failed to process: {str(e)}"
                    )
                )
            finally:
                await file.close() # Важно закрыть файл

        return upload_statuses