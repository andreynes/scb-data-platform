# etl/dags/file_processing_dag.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

# --- ИМПОРТЫ (ИСПРАВЛЕНО) ---
# Теперь Python будет искать модули относительно /opt/airflow, где лежит папка etl_src
from etl.src.extract import mongo_extractor
from etl.src.transform.parsing import parser_orchestrator
from etl.src.transform.validation import validator as data_validator
from etl.src.load import clickhouse_loader, mongo_updater
from etl.src.llm.llm_client import LLMClient
from etl.src.ontology import ontology_loader
from etl.src.utils.logging_utils import setup_etl_logger
from etl.src.utils.db_clients import get_mongo_db_client, get_clickhouse_client
from etl.src.transform.null_handling import null_handler
# -----------------

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
    Включает обработку NULL-значений и опциональное использование LLM.
    """

    @task
    def get_document_info() -> Dict[str, Any]:
        """Извлекает метаданные документа и параметры запуска из ОЗЕРА."""
        context = get_current_context()
        document_id = context["params"].get("document_id")
        if not document_id:
            raise ValueError("`document_id` must be provided in DAG params")

        mongo_db = get_mongo_db_client()
        metadata = mongo_extractor.get_document_metadata_sync(document_id, mongo_db)
        if not metadata:
            raise ValueError(f"Metadata not found for document_id: {document_id}")
        
        mongo_updater.update_processing_status_sync(document_id, "Processing", db_client=mongo_db)
        
        metadata['use_llm'] = context["params"].get("use_llm", False)
        metadata['target_ontology_version'] = context["params"].get("ontology_version")
        
        return metadata

    @task
    def parse_data(document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Задача парсинга. Может использовать прямой парсер или LLM."""
        mongo_db = get_mongo_db_client()
        
        target_version = document_metadata.get('target_ontology_version')
        if target_version:
             ontology_schema = ontology_loader.get_ontology_schema_by_version_sync(target_version, mongo_db)
        else:
             ontology_schema = ontology_loader.get_current_ontology_schema_sync(mongo_db)

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

        # Обрати внимание, что твой orchestrator асинхронный, а DAG выполняется синхронно.
        # asyncio.run() - это правильный способ запустить async код в sync контексте.
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

    @task
    def validate_data(parsing_result: dict) -> dict:
        """Валидирует распарсенные данные по схеме онтологии."""
        parsed_data = parsing_result["parsed_data"]
        ontology_schema = parsing_result["ontology_schema"]
        
        if not parsed_data:
            logger.info("No data to validate, skipping.")
            parsing_result["validated_data"] = []
            return parsing_result

        mongo_db = get_mongo_db_client()
        vocabularies = ontology_loader.get_all_vocabularies_sync(ontology_schema, mongo_db)

        validated_data = data_validator.validate_cleaned_data(
            cleaned_data=parsed_data,
            ontology_schema=ontology_schema,
            ontology_vocabularies=vocabularies
        )
        parsing_result["validated_data"] = validated_data
        return parsing_result
    
    @task
    def handle_nulls(validation_result: dict) -> dict:
        """Обрабатывает семантику NULL-значений в данных после валидации."""
        validated_data = validation_result.get("validated_data")
        ontology_schema = validation_result.get("ontology_schema")

        if not validated_data or not ontology_schema:
            logger.info("No data for NULL processing, skipping.")
            validation_result["processed_data"] = []
            return validation_result
        
        processed_data = null_handler.process_null_semantics(
            validated_data=validated_data,
            ontology_schema=ontology_schema
        )
        validation_result["processed_data"] = processed_data
        return validation_result

    @task
    def load_to_warehouse(null_handling_result: dict):
        """Загружает валидированные и обработанные данные в ClickHouse и обновляет статус в MongoDB."""
        data_to_load = null_handling_result.get("processed_data") 
        document_id = null_handling_result["document_id"]
        ontology_schema = null_handling_result["ontology_schema"]
        
        mongo_db = get_mongo_db_client()
        
        if not data_to_load:
            logger.warning(f"No processed data to load for document {document_id}. Updating status to Processed.")
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_db)
            return

        ch_client = get_clickhouse_client()
        try:
            clickhouse_loader.load_data_to_warehouse_sync(
                data_to_load=data_to_load,
                ch_client=ch_client,
                original_document_id=document_id,
                ontology_version=ontology_schema['version']
            )
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_db)
            logger.info(f"Successfully loaded data for document {document_id} to Warehouse.")
        except Exception as e:
            logger.error(f"Failed to load data to Warehouse for document {document_id}. Error: {e}", exc_info=True)
            mongo_updater.update_processing_status_sync(document_id, "Error", error_message=str(e), db_client=mongo_db)
            raise

    # --- Последовательность выполнения ---
    doc_info = get_document_info()
    parsing_result = parse_data(doc_info)
    validated_result = validate_data(parsing_result)
    null_result = handle_nulls(validated_result)
    load_to_warehouse(null_result)

# Создаем экземпляр DAG
file_processing_dag = file_processing()