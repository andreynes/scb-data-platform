from __future__ import annotations

import pendulum 
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException

# --- Импорт наших ETL модулей ---
from etl_src.utils.logging_utils import setup_etl_logger
from etl_src.utils.config_utils import etl_settings

from etl_src.extract import mongo_extractor
from etl_src.ontology import ontology_loader
from etl_src.transform.parsing import parser_orchestrator
from etl_src.transform.cleaning import cleaner 
from etl_src.transform.validation import validator 
from etl_src.transform.null_handling import null_handler 
from etl_src.load import clickhouse_loader, mongo_updater 

# --- Импорт клиентов БД ---
from pymongo import MongoClient
import clickhouse_connect

# ... (весь блок с глобальными переменными остается без изменений) ...
MONGO_CONN_URI = etl_settings.MONGO_DB_URL
MONGO_DB_NAME = etl_settings.MONGO_DB_NAME
RAW_DATA_LAKE_COLLECTION = etl_settings.RAW_DATA_LAKE_COLLECTION
ONTOLOGY_SCHEMAS_COLLECTION = etl_settings.ONTOLOGY_SCHEMAS_COLLECTION
ONTOLOGY_VOCABULARIES_COLLECTION = etl_settings.ONTOLOGY_VOCABULARIES_COLLECTION
ONTOLOGY_STATUS_COLLECTION = etl_settings.ONTOLOGY_STATUS_COLLECTION


CLICKHOUSE_HOST = etl_settings.CLICKHOUSE_HOST
CLICKHOUSE_PORT = etl_settings.CLICKHOUSE_PORT
CLICKHOUSE_USER = etl_settings.CLICKHOUSE_USER
CLICKHOUSE_PASSWORD = etl_settings.CLICKHOUSE_PASSWORD
CLICKHOUSE_DB = etl_settings.CLICKHOUSE_DB
CLICKHOUSE_ATOMIC_TABLE = etl_settings.CLICKHOUSE_ATOMIC_TABLE

dag_logger = setup_etl_logger('file_processing_dag')

# --- Определение DAG ---
@dag(
    dag_id="file_processing_dag",
    schedule=None, 
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl", "core"],
    default_args={
        "owner": "airflow",
        "retries": 1, 
        "retry_delay": timedelta(minutes=1),
    },
    doc_md=__doc__
)
def file_processing_workflow():
    """
    ### Основной DAG для обработки файлов
    ... (документация без изменений) ...
    """

    @task
    def get_file_info_and_set_processing(dag_run=None):
        """Извлекает метаданные документа и JSON, обновляет статус на 'Processing'."""
        # ... (код таска без изменений) ...
        document_id = dag_run.conf.get("document_id")
        if not document_id:
            dag_logger.error("document_id not provided in DAG run configuration.")
            raise ValueError("document_id is required")
        
        dag_logger.info(f"Starting processing for document_id: {document_id}")
        
        client = MongoClient(MONGO_CONN_URI)
        db = client[MONGO_DB_NAME]
        
        mongo_updater.update_document_processing_status(
            mongo_db=db,
            document_id=document_id,
            status="Processing",
            raw_data_lake_collection_name=RAW_DATA_LAKE_COLLECTION
        )
        
        metadata = mongo_extractor.get_document_metadata(document_id, db, RAW_DATA_LAKE_COLLECTION)
        if not metadata:
            mongo_updater.update_document_processing_status(db, document_id, "Error_Extracting", "Metadata not found", RAW_DATA_LAKE_COLLECTION)
            raise ValueError(f"Metadata not found for document_id: {document_id}")
        
        client.close()
        dag_logger.info(f"Extracted metadata for document_id: {document_id}")
        return {"document_id": document_id, "metadata": metadata}


    @task
    def load_active_ontology():
        """Загружает активную схему онтологии и справочники."""
        client = MongoClient(MONGO_CONN_URI)
        db = client[MONGO_DB_NAME]
        
        collection_names_cfg = {
            "status": ONTOLOGY_STATUS_COLLECTION,
            "schemas": ONTOLOGY_SCHEMAS_COLLECTION,
            "vocabularies": ONTOLOGY_VOCABULARIES_COLLECTION,
        }

        # _get_active_ontology_version_id остается как есть, он нам нужен для загрузки справочников
        active_version_id = ontology_loader._get_active_ontology_version_id(db, collection_names_cfg)
        if not active_version_id:
            raise ValueError("No active ontology version found.")
        
        #
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # Убираем лишний аргумент. Функция сама найдет активную версию.
        #
        schema = ontology_loader.get_current_ontology_schema(db, collection_names_cfg)
        
        # Исправляем вызов для get_multiple_vocabularies. 
        # Первый аргумент - список имен, передаем None, если нужно загрузить все.
        # В вашем коде был None, но это может быть неверно, зависит от реализации.
        # Для безопасности пока передадим пустой список, чтобы он ничего не загружал, если не нужно.
        # Если вам нужны все справочники, реализация get_multiple_vocabularies должна это поддерживать.
        vocabularies = ontology_loader.get_multiple_vocabularies([], db, active_version_id, collection_names_cfg)
        
        client.close()
        if not schema:
             raise ValueError("Failed to load active ontology schema.")
        dag_logger.info(f"Loaded active ontology version: {active_version_id}")
        return {"ontology_schema": schema, "ontology_vocabularies": vocabularies, "ontology_version": active_version_id}

    # ... (остальные таски и определение потока остаются без изменений) ...
    @task
    def parse_data(file_info_and_metadata: dict, ontology_info: dict):
        # ...
        pass
    @task
    def clean_data(parsed_data_info: dict, ontology_info: dict):
        # ...
        pass
    @task
    def validate_data(cleaned_data_info: dict, ontology_info: dict):
        # ...
        pass
    @task
    def handle_nulls(validated_data_info: dict, ontology_info: dict):
        # ...
        pass
    @task
    def load_to_warehouse(null_handled_data_info: dict, ontology_info: dict):
        # ...
        pass
    @task(trigger_rule="all_done")
    def update_final_status(load_result: Optional[dict], document_id: str, validation_errors: list):
        # ...
        pass

    # --- Определение потока задач ---
    file_info = get_file_info_and_set_processing()
    ontology = load_active_ontology()
    
    parsed = parse_data(file_info_and_metadata=file_info, ontology_info=ontology)
    cleaned = clean_data(parsed_data_info=parsed, ontology_info=ontology)
    validated = validate_data(cleaned_data_info=cleaned, ontology_info=ontology)
    null_handled = handle_nulls(validated_data_info=validated, ontology_info=ontology)
    
    load_result = load_to_warehouse(null_handled_data_info=null_handled, ontology_info=ontology)
    
    update_final_status(
        load_result=load_result, 
        document_id=file_info["document_id"],
        validation_errors=validated["validation_errors"]
    )

file_processing_dag = file_processing_workflow()