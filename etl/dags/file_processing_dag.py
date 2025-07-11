import asyncio
from datetime import datetime
from typing import Dict, Any

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
# Все импорты начинаются с src.
from src.extract import mongo_extractor
from src.load import clickhouse_loader, mongo_updater
from src.ontology import ontology_loader
from src.transform.cleaning import cleaner
from src.transform.null_handling import null_handler
from src.transform.parsing import parser_orchestrator
from src.transform.validation import validator as data_validator
from src.utils.db_clients import get_mongo_db_client, get_clickhouse_client
from src.utils.logging_utils import setup_etl_logger
# -----------------

logger = setup_etl_logger(__name__)

@dag(
    dag_id="file_processing_dag",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "document_id": Param(None, type=["null", "string"]),
        "use_llm": Param(False, type="boolean"),
        "ontology_version": Param(None, type=["null", "string"]),
    },
    tags=["etl", "core"],
)
def file_processing():
    # ... (остальной код DAG остается без изменений) ...

    @task(task_id="get_document_info")
    def get_document_info_task() -> Dict[str, Any]:
        context = get_current_context()
        document_id = context["params"].get("document_id")
        if not document_id:
            raise ValueError("`document_id` must be provided in DAG params")

        logger.info(f"Starting processing for document_id: {document_id}")
        mongo_db = get_mongo_db_client()
        metadata = mongo_extractor.get_document_metadata_sync(document_id, mongo_db)
        if not metadata:
            raise ValueError(f"Metadata not found for document_id: {document_id}")
        
        mongo_updater.update_processing_status_sync(document_id, "Processing", db_client=mongo_db)
        
        metadata['use_llm'] = context["params"].get("use_llm", False)
        metadata['target_ontology_version'] = context["params"].get("ontology_version")
        
        return metadata

    @task(task_id="parse_and_clean_data")
    def parse_and_clean_data_task(document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        mongo_db = get_mongo_db_client()
        target_version = document_metadata.get('target_ontology_version')
        ontology_schema = ontology_loader.get_ontology_schema_sync(mongo_db, target_version)

        if not ontology_schema:
            raise RuntimeError(f"Could not load ontology schema (target: {target_version or 'active'}).")

        parsed_data = asyncio.run(
            parser_orchestrator.parse_document_content(
                document_metadata=document_metadata,
                ontology_schema=ontology_schema,
            )
        )
        cleaned_data = cleaner.clean_parsed_data(parsed_data or [])

        return {
            "cleaned_data": cleaned_data,
            "ontology_schema": ontology_schema,
            "document_id": document_metadata.get('_id')
        }

    @task(task_id="validate_and_handle_nulls")
    def validate_and_handle_nulls_task(parsing_result: dict) -> dict:
        cleaned_data = parsing_result["cleaned_data"]
        ontology_schema = parsing_result["ontology_schema"]
        
        if not cleaned_data:
            logger.info("No data to validate, skipping.")
            parsing_result["processed_data"] = []
            return parsing_result

        mongo_db = get_mongo_db_client()
        vocabularies = ontology_loader.get_all_vocabularies_sync(ontology_schema, mongo_db)

        validation_results = data_validator.validate_data(
            data=cleaned_data, ontology_schema=ontology_schema, ontology_vocabularies=vocabularies
        )
        processed_data = null_handler.process_null_semantics(
            validated_data=validation_results['valid_data'], validation_errors=validation_results['errors']
        )
        
        parsing_result["processed_data"] = processed_data
        return parsing_result

    @task(task_id="load_to_warehouse", trigger_rule="all_done")
    def load_to_warehouse_task(processed_result: dict):
        context = get_current_context()
        dag_run = context["dag_run"]
        
        data_to_load = processed_result.get("processed_data") 
        document_id = processed_result["document_id"]
        ontology_schema = processed_result["ontology_schema"]
        
        mongo_db = get_mongo_db_client()
        
        if any(ti.state == 'failed' for ti in dag_run.get_task_instances()):
             error_message = "ETL process failed in one of the upstream tasks."
             logger.error(error_message)
             mongo_updater.update_processing_status_sync(document_id, "Error", error_message=error_message, db_client=mongo_db)
             return

        if not data_to_load:
            logger.warning(f"No processed data to load for document {document_id}.")
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_db)
            return

        ch_client = get_clickhouse_client()
        try:
            clickhouse_loader.load_data_to_warehouse_sync(
                data_to_load=data_to_load, ch_client=ch_client,
                original_document_id=document_id, ontology_version=ontology_schema['version']
            )
            mongo_updater.update_processing_status_sync(document_id, "Processed", db_client=mongo_db)
            logger.info(f"Successfully loaded data for document {document_id}.")
        except Exception as e:
            logger.error(f"Failed to load data to Warehouse for {document_id}. Error: {e}", exc_info=True)
            mongo_updater.update_processing_status_sync(document_id, "Error", error_message=str(e), db_client=mongo_db)
            raise

    doc_info = get_document_info_task()
    parsing_result = parse_and_clean_data_task(doc_info)
    validated_result = validate_and_handle_nulls_task(parsing_result)
    load_to_warehouse_task(validated_result)

file_processing_dag = file_processing()