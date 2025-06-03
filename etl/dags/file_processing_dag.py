# etl/dags/file_processing_dag.py
from __future__ import annotations

import pendulum
import logging

from airflow.decorators import dag, task
from airflow.models.param import Param # Для Airflow 2.2+ для передачи параметров

logger = logging.getLogger(__name__)

@dag(
    dag_id="file_processing_dag", # Важно: имя DAG, которое будет триггерить бэкенд
    schedule=None, # Запускается только по триггеру
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"), # Измени на актуальную дату начала
    catchup=False,
    tags=["etl", "core", "file-processing"],
    # Ожидаем параметр document_id при запуске извне
    params={
        "document_id": Param(
            None, # Значение по умолчанию, если не передано (хотя мы всегда будем передавать)
            type=["null", "string"], 
            description="ID документа из ОЗЕРА (MongoDB) для обработки"
        )
    }
)
def file_processing_dag_definition(): # Изменил имя функции для ясности, что это определение DAG
    """
    ### DAG для Обработки Загруженных Файлов

    Этот DAG инициируется после загрузки нового файла в систему.
    Он получает `document_id` файла из ОЗЕРА (MongoDB) в качестве параметра.

    **На данном этапе (MVP - пустой DAG):**
    - Логирует полученный `document_id`.
    - Не выполняет реальной обработки файла (парсинг, загрузка в СКЛАД и т.д.).
    """

    @task
    def log_received_document_id_task(dag_run=None):
        """
        Логирует ID документа, полученный при запуске DAG.
        В будущем здесь начнется реальная обработка.
        """
        document_id = dag_run.conf.get("document_id") if dag_run and dag_run.conf else None
        
        if document_id:
            logger.info(f"File Processing DAG triggered for document_id: {document_id}")
            print(f"File Processing DAG triggered for document_id: {document_id}") # Также в stdout для логов Docker
        else:
            logger.warning("File Processing DAG triggered but 'document_id' was not found in DAG run configuration.")
            print("File Processing DAG triggered but 'document_id' was not found in DAG run configuration.")
            # Можно здесь даже фейлить задачу, если document_id обязателен
            # raise ValueError("document_id is required and was not provided in DAG run conf.")
        
        return document_id # Возвращаем для возможного использования в XCom другими задачами

    # Вызываем задачу
    log_task_result = log_received_document_id_task()

# Инстанцируем DAG
file_processing_dag = file_processing_dag_definition()