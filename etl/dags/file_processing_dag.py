from __future__ import annotations

import pendulum 
from datetime import timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
# Если не используете декораторы, то:
# from airflow.models.dag import DAG
# from airflow.operators.python import PythonOperator

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

# --- Глобальные переменные/настройки DAG ---
# (Лучше брать из Airflow Variables или etl_settings)
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

# --- Логгер для DAG ---
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
    doc_md=__doc__ # Если у вас есть документация в docstring модуля
)
def file_processing_workflow():
    """
    ### Основной DAG для обработки файлов
    Этот DAG извлекает данные о файле из MongoDB, парсит его содержимое,
    очищает, валидирует, обрабатывает NULL-значения и загружает в ClickHouse.
    Ожидает параметр `document_id` в конфигурации запуска.
    """

    @task
    def get_file_info_and_set_processing(dag_run=None):
        """Извлекает метаданные документа и JSON, обновляет статус на 'Processing'."""
        document_id = dag_run.conf.get("document_id")
        if not document_id:
            dag_logger.error("document_id not provided in DAG run configuration.")
            raise ValueError("document_id is required")
        
        dag_logger.info(f"Starting processing for document_id: {document_id}")
        
        client = MongoClient(MONGO_CONN_URI)
        db = client[MONGO_DB_NAME]
        
        # Обновляем статус на Processing
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

        # Для MVP JSON должен быть уже в метаданных
        # file_content_json = mongo_extractor.get_json_representation_from_metadata(metadata)
        # if not file_content_json:
        #     # Здесь может быть логика извлечения и парсинга файла, если JSON нет.
        #     # Для MVP ожидаем, что JSON уже есть.
        #     mongo_updater.update_document_processing_status(db, document_id, "Error_Extracting", "JSON representation not found", RAW_DATA_LAKE_COLLECTION)
        #     raise ValueError(f"JSON representation not found for document_id: {document_id}")
        
        client.close()
        dag_logger.info(f"Extracted metadata for document_id: {document_id}")
        # Возвращаем метаданные, т.к. json_representation уже внутри них
        return {"document_id": document_id, "metadata": metadata}


    @task
    def load_active_ontology():
        """Загружает активную схему онтологии и справочники."""
        client = MongoClient(MONGO_CONN_URI)
        db = client[MONGO_DB_NAME]
        
        # Используем collection_names из config_utils или задаем по умолчанию
        collection_names_cfg = {
            "status": ONTOLOGY_STATUS_COLLECTION,
            "schemas": ONTOLOGY_SCHEMAS_COLLECTION,
            "vocabularies": ONTOLOGY_VOCABULARIES_COLLECTION,
        }

        active_version_id = ontology_loader._get_active_ontology_version_id(db, collection_names_cfg)
        if not active_version_id:
            raise ValueError("No active ontology version found.")
        
        schema = ontology_loader.get_current_ontology_schema(db, collection_names_cfg, active_version_id_override=active_version_id)
        # Для MVP загрузим все справочники, т.к. схема простая
        # В будущем можно загружать только нужные на основе schema
        vocabularies = ontology_loader.get_multiple_vocabularies(None, db, active_version_id, collection_names_cfg)
        
        client.close()
        if not schema:
             raise ValueError("Failed to load active ontology schema.")
        dag_logger.info(f"Loaded active ontology version: {active_version_id}")
        return {"ontology_schema": schema, "ontology_vocabularies": vocabularies, "ontology_version": active_version_id}

    @task
    def parse_data(file_info_and_metadata: dict, ontology_info: dict):
        """Парсит JSON-представление документа."""
        document_id = file_info_and_metadata["document_id"]
        metadata = file_info_and_metadata["metadata"]
        # ontology_schema = ontology_info["ontology_schema"] # Пока не используется в MVP парсере

        dag_logger.info(f"Parsing data for document_id: {document_id}")
        # Для MVP parser_orchestrator ожидает, что json_representation уже в metadata
        parsed_data_list = parser_orchestrator.parse_document_content(metadata)
        if not parsed_data_list: # Если парсинг вернул пустой список (возможно ошибка или пустой файл)
             dag_logger.warning(f"Parsing returned no data for document_id: {document_id}")
             # Решаем, считать ли это ошибкой или просто нет данных для загрузки
             # Для MVP, если парсинг не дал данных, это может быть не ошибка этапа,
             # а просто файл не содержит табличных данных в ожидаемом JSON формате.
             # Последующие шаги обработают пустой список.

        dag_logger.info(f"Parsed {len(parsed_data_list)} rows for document_id: {document_id}")
        return {"document_id": document_id, "parsed_data": parsed_data_list, "ontology_version": ontology_info["ontology_version"]}

    @task
    def clean_data(parsed_data_info: dict, ontology_info: dict):
        """Очищает распарсенные данные."""
        document_id = parsed_data_info["document_id"]
        parsed_data = parsed_data_info["parsed_data"]
        ontology_schema = ontology_info["ontology_schema"]

        if not parsed_data:
            dag_logger.info(f"No parsed data to clean for document_id: {document_id}")
            return {"document_id": document_id, "cleaned_data": [], "ontology_version": parsed_data_info["ontology_version"]}

        dag_logger.info(f"Cleaning data for document_id: {document_id}")
        cleaned_data_list = cleaner.clean_parsed_data(parsed_data, ontology_schema)
        dag_logger.info(f"Cleaned data for document_id: {document_id}")
        return {"document_id": document_id, "cleaned_data": cleaned_data_list, "ontology_version": parsed_data_info["ontology_version"]}

    @task
    def validate_data(cleaned_data_info: dict, ontology_info: dict):
        """Валидирует очищенные данные."""
        document_id = cleaned_data_info["document_id"]
        cleaned_data = cleaned_data_info["cleaned_data"]
        ontology_schema = ontology_info["ontology_schema"]
        ontology_vocabularies = ontology_info["ontology_vocabularies"]

        if not cleaned_data:
            dag_logger.info(f"No cleaned data to validate for document_id: {document_id}")
            return {"document_id": document_id, "validated_data": [], "validation_errors": [], "ontology_version": cleaned_data_info["ontology_version"]}

        dag_logger.info(f"Validating data for document_id: {document_id}")
        validated_data_list, validation_errors = validator.validate_cleaned_data(
            cleaned_data, ontology_schema, ontology_vocabularies, document_id
        )
        dag_logger.info(f"Validated data for document_id: {document_id}. Errors found: {len(validation_errors)}")
        if validation_errors:
            dag_logger.warning(f"Validation errors for doc_id {document_id}: {validation_errors[:3]}") # Логируем первые 3 ошибки

        return {"document_id": document_id, "validated_data": validated_data_list, "validation_errors": validation_errors, "ontology_version": cleaned_data_info["ontology_version"]}
    
    @task
    def handle_nulls(validated_data_info: dict, ontology_info: dict):
        """Обрабатывает NULL-семантику."""
        document_id = validated_data_info["document_id"]
        validated_data = validated_data_info["validated_data"]
        # validation_errors = validated_data_info["validation_errors"] # может понадобиться
        ontology_schema = ontology_info["ontology_schema"]

        if not validated_data:
            dag_logger.info(f"No validated data for NULL handling for document_id: {document_id}")
            return {"document_id": document_id, "data_for_load": [], "ontology_version": validated_data_info["ontology_version"]}

        dag_logger.info(f"Handling NULLs for document_id: {document_id}")
        # null_handler.process_null_semantics может ожидать validation_results, если он их использует.
        # Для MVP, предположим, он может работать только с validated_data и ontology_schema
        data_for_load = null_handler.process_null_semantics(validated_data, ontology_schema, None) # Передаем None для validation_results
        dag_logger.info(f"NULLs handled for document_id: {document_id}")
        return {"document_id": document_id, "data_for_load": data_for_load, "ontology_version": validated_data_info["ontology_version"]}


    @task(trigger_rule="all_done") # Запускается всегда, чтобы обновить статус
    def update_final_status(load_result: Optional[dict], document_id: str, validation_errors: list):
        """Обновляет финальный статус документа в MongoDB."""
        # load_result может быть None, если предыдущая задача была пропущена или упала
        # и мы не передали XCom явно. В данном случае, если load_to_warehouse упадет, он не вернет XCom
        
        # Статус по умолчанию - ошибка, если load_result не говорит об успехе
        final_status = "Error_Loading"
        error_msg = "Failed to load data to warehouse or previous step failed."
        processing_details_dict = {"validation_errors_count": len(validation_errors)}

        if load_result and load_result.get("load_successful"):
            final_status = "Processed"
            error_msg = None # Очищаем сообщение об ошибке
            processing_details_dict["rows_loaded"] = load_result.get("rows_loaded", 0)
        elif validation_errors: # Если загрузка не удалась, но были ошибки валидации
             final_status = "Error_Validation" # Или другой подходящий статус
             error_msg = f"Validation errors occurred: {len(validation_errors)} issues. First 3: {validation_errors[:3]}"


        client = MongoClient(MONGO_CONN_URI)
        db = client[MONGO_DB_NAME]
        mongo_updater.update_document_processing_status(
            mongo_db=db,
            document_id=document_id,
            status=final_status,
            error_message=error_msg,
            processing_details=processing_details_dict,
            raw_data_lake_collection_name=RAW_DATA_LAKE_COLLECTION
        )
        client.close()
        dag_logger.info(f"Final status for document_id {document_id} set to {final_status}")
        if final_status != "Processed":
            # Если были ошибки, можно явно провалить DAG, чтобы он был помечен как failed
            raise AirflowException(f"ETL process failed for document {document_id} with status {final_status}")


    @task
    def load_to_warehouse(null_handled_data_info: dict, ontology_info: dict):
        """Загружает данные в ClickHouse."""
        document_id = null_handled_data_info["document_id"]
        data_for_load = null_handled_data_info["data_for_load"]
        ontology_schema = ontology_info["ontology_schema"]
        ontology_version = null_handled_data_info["ontology_version"]

        if not data_for_load:
            dag_logger.info(f"No data to load to warehouse for document_id: {document_id}")
            return {"document_id": document_id, "load_successful": True, "rows_loaded": 0} # Считаем успехом

        dag_logger.info(f"Loading data to warehouse for document_id: {document_id}")
        
        ch_client = None
        try:
            ch_client = clickhouse_connect.get_client(
                host=CLICKHOUSE_HOST, 
                port=CLICKHOUSE_PORT, 
                username=CLICKHOUSE_USER, 
                password=CLICKHOUSE_PASSWORD, 
                database=CLICKHOUSE_DB # Убедитесь, что база данных существует
            )
            
            success = clickhouse_loader.load_data_to_warehouse(
                data_to_load, 
                ch_client, 
                CLICKHOUSE_ATOMIC_TABLE, 
                ontology_schema, 
                document_id,
                ontology_version
            )
            if success:
                dag_logger.info(f"Successfully loaded data to warehouse for document_id: {document_id}")
                return {"document_id": document_id, "load_successful": True, "rows_loaded": len(data_for_load)}
            else:
                dag_logger.error(f"Failed to load data to warehouse for document_id: {document_id}")
                return {"document_id": document_id, "load_successful": False}
        except Exception as e:
            dag_logger.error(f"Exception during ClickHouse load for doc_id {document_id}: {e}")
            return {"document_id": document_id, "load_successful": False, "error": str(e)}
        finally:
            if ch_client:
                ch_client.close()
    
    # --- Определение потока задач ---
    file_info = get_file_info_and_set_processing()
    ontology = load_active_ontology()
    
    parsed = parse_data(file_info_and_metadata=file_info, ontology_info=ontology)
    cleaned = clean_data(parsed_data_info=parsed, ontology_info=ontology)
    validated = validate_data(cleaned_data_info=cleaned, ontology_info=ontology)
    null_handled = handle_nulls(validated_data_info=validated, ontology_info=ontology)
    
    load_result = load_to_warehouse(null_handled_data_info=null_handled, ontology_info=ontology)
    
    # Передаем document_id и validation_errors в финальную задачу
    update_final_status(
        load_result=load_result, 
        document_id=file_info["document_id"], # Получаем из XCom задачи get_file_info
        validation_errors=validated["validation_errors"] # Получаем из XCom задачи validate_data
    )

file_processing_dag = file_processing_workflow()