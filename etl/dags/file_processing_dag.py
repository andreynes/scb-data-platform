# etl/dags/file_processing_dag.py

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

# --- Импорты всех наших ETL модулей ---
from etl.src.extract import mongo_extractor
from etl.src.transform.parsing import parser_orchestrator
from etl.src.transform.validation import validator as data_validator # <-- ДОБАВЛЕНО
from etl.src.load import clickhouse_loader, mongo_updater           # <-- ДОБАВЛЕНО
from etl.src.llm.llm_client import LLMClient
from etl.src.ontology import ontology_loader
from etl.src.utils.logging_utils import setup_etl_logger          # <-- ДОБАВЛЕНО

# --- Импорты клиентов БД ---
from etl.src.db_clients import get_mongo_db_client, get_clickhouse_client

logger = setup_etl_logger(__name__)

@dag(
    dag_id="file_processing_dag",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "document_id": Param(None, type="string"),
        "use_llm": Param(False, type="boolean", description="Принудительно использовать LLM для парсинга"),
        "ontology_version": Param(None, type=["null", "string"], description="Конкретная версия онтологии для репарсинга"),
    },
    tags=["etl", "core"],
)
def file_processing():
    """
    DAG для полной обработки одного файла: от извлечения из ОЗЕРА до загрузки в СКЛАД.
    Включает опциональное использование LLM.
    """

    @task
    def get_document_info() -> Dict[str, Any]:
        """Извлекает метаданные документа и параметры запуска из ОЗЕРА."""
        context = get_current_context()
        document_id = context["params"].get("document_id")
        if not document_id:
            raise ValueError("`document_id` must be provided in DAG params")

        mongo_client = get_mongo_db_client()
        metadata = mongo_extractor.get_document_metadata_sync(document_id, mongo_client)
        if not metadata:
            raise ValueError(f"Metadata not found for document_id: {document_id}")
        
        # Обновляем статус на "в обработке"
        mongo_updater.update_processing_status_sync(document_id, "Processing", db_client=mongo_client)
        
        # Добавляем параметры запуска в метаданные для передачи по XCom
        metadata['use_llm'] = context["params"].get("use_llm", False)
        metadata['target_ontology_version'] = context["params"].get("ontology_version")
        
        return metadata

    @task
    def parse_data(document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Задача парсинга. Может использовать прямой парсер или LLM."""
        mongo_client = get_mongo_db_client()
        
        target_version = document_metadata.get('target_ontology_version')
        if target_version:
             ontology_schema = ontology_loader.get_ontology_schema_by_version_sync(target_version, mongo_client)
        else:
             ontology_schema = ontology_loader.get_current_ontology_schema_sync(mongo_client)

        if not ontology_schema:
            raise RuntimeError(f"Could not load ontology schema (target version: {target_version or 'active'}).")
            
        use_llm_flag = document_metadata.get('use_llm', False)
        llm_client_instance = None

        if use_llm_flag:
            llm_provider = os.getenv("LLM_PROVIDER")
            llm_api_key = os.getenv("LLM_API_KEY")
            llm_parsing_model = os.getenv("LLM_PARSING_MODEL_NAME")

            if not all([llm_provider, llm_api_key, llm_parsing_model]):
                raise ValueError("LLM configuration is missing in environment variables.")
            
            llm_client_instance = LLMClient(provider=llm_provider, api_key=llm_api_key, model_name=llm_parsing_model)

        parsed_data = asyncio.run(
            parser_orchestrator.parse_document_content(
                document_metadata=document_metadata,
                ontology_schema=ontology_schema,
                use_llm=use_llm_flag,
                llm_client=llm_client_instance
            )
        )
        
        if not parsed_data:
            logger.warning(f"Parsing returned no data for document {document_metadata.get('_id')}")

        return {
            "parsed_data": parsed_data,
            "ontology_schema": ontology_schema,
            "document_id": document_metadata.get('_id')
        }

    # <-- НАЧАЛО НОВЫХ/ОБНОВЛЕННЫХ ЗАДАЧ -->
    @task
    def validate_data(parsing_result: dict) -> dict:
        """Валидирует распарсенные данные по схеме онтологии."""
        parsed_data = parsing_result["parsed_data"]
        ontology_schema = parsing_result["ontology_schema"]
        
        if not parsed_data:
            logger.info("No data to validate, skipping.")
            return parsing_result # Передаем дальше, чтобы обновить статус

        mongo_client = get_mongo_db_client()
        # Загружаем справочники, необходимые для валидации
        vocabularies = ontology_loader.get_all_vocabularies_sync(ontology_schema, mongo_client)

        validated_data = data_validator.validate_cleaned_data(
            cleaned_data=parsed_data,
            ontology_schema=ontology_schema,
            ontology_vocabularies=vocabularies
        )
        parsing_result["validated_data"] = validated_data
        return parsing_result

    @task
    def load_to_warehouse(validation_result: dict):
        """Загружает валидированные данные в ClickHouse и обновляет статус в MongoDB."""
        validated_data = validation_result.get("validated_data")
        document_id = validation_result["document_id"]
        ontology_schema = validation_result["ontology_schema"]
        
        mongo_client = get_mongo_db_client()
        
        if not validated_data:
            logger.warning(f"No validated data to load for document {document_id}. Updating status to Processed.")
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_client)
            return

        ch_client = get_clickhouse_client()
        try:
            clickhouse_loader.load_data_to_warehouse_sync(
                data_to_load=validated_data,
                ch_client=ch_client,
                original_document_id=document_id,
                ontology_version=ontology_schema['version']
            )
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_client)
            logger.info(f"Successfully loaded data for document {document_id} to Warehouse.")
        except Exception as e:
            logger.error(f"Failed to load data to Warehouse for document {document_id}. Error: {e}", exc_info=True)
            mongo_updater.update_processing_status_sync(document_id, "Error", error_message=str(e), db_client=mongo_client)
            raise # Провалить задачу в Airflow
    # <-- КОНЕЦ НОВЫХ/ОБНОВЛЕННЫХ ЗАДАЧ -->

    # --- Определение последовательности выполнения ---
    doc_info = get_document_info()
    parsing_result = parse_data(doc_info)
    validated_result = validate_data(parsing_result)
    load_to_warehouse(validated_result) # Конечная задача

# Создаем экземпляр DAG
file_processing_dag = file_processing()