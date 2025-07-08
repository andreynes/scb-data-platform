# backend/app/services/file_processing_service.py

import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import UploadFile

# ИСПРАВЛЕНО: Корректные абсолютные импорты
from clients import airflow_client
from repositories.data_lake_repo import DataLakeRepo
from schemas.file_schemas import FileUploadStatusSchema
from schemas.user_schemas import UserSchema

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self, data_lake_repo: DataLakeRepo):
        self.data_lake_repo = data_lake_repo

    async def process_uploaded_files(
        self, files: List[UploadFile], uploader: UserSchema
    ) -> List[FileUploadStatusSchema]:
        statuses: List[FileUploadStatusSchema] = []

        for file in files:
            document_id = str(uuid.uuid4())
            metadata = {
                "_id": document_id,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "uploader_id": uploader.id,
                "upload_timestamp": datetime.utcnow(),
                "processing_status": "Accepted",
            }

            try:
                await self.data_lake_repo.save_file_metadata(metadata)
                logger.info(f"Saved metadata for document_id: {document_id}")

                dag_conf = {"document_id": document_id}
                is_triggered = await airflow_client.trigger_dag(
                    dag_id="file_processing_dag", conf=dag_conf
                )

                if is_triggered:
                    await self.data_lake_repo.update_processing_status(document_id, "Processing")
                    logger.info(f"Successfully triggered DAG for document {document_id}")
                    statuses.append(
                        FileUploadStatusSchema(
                            filename=file.filename,
                            document_id=document_id,
                            status="Processing",
                        )
                    )
                else:
                    error_msg = "Failed to trigger ETL process."
                    await self.data_lake_repo.update_processing_status(
                        document_id, "Error", error_message=error_msg
                    )
                    logger.error(f"DAG trigger failed for document {document_id}")
                    statuses.append(
                        FileUploadStatusSchema(
                            filename=file.filename,
                            document_id=document_id,
                            status="Error",
                            error_message=error_msg,
                        )
                    )

            except Exception as e:
                logger.error(
                    f"Error processing file {file.filename}. Assigned document_id: {document_id}. Error: {e}",
                    exc_info=True,
                )
                statuses.append(
                    FileUploadStatusSchema(
                        filename=file.filename,
                        document_id=document_id,
                        status="Error",
                        error_message=str(e),
                    )
                )

        return statuses