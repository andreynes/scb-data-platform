import sys
import os
import logging # <--- ДОБАВЛЕНО: Стандартный модуль логирования
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.models.param import Param # <--- ДОБАВЛЕНО: Для определения параметров DAG
# from airflow.exceptions import AirflowSkipException # Пока не используется

# Добавляем путь к нашим ETL модулям в PYTHONPATH
# Путь должен быть относительно AIRFLOW_HOME (обычно /opt/airflow)
sys.path.append('/opt/airflow') 

# Теперь можно импортировать наши модули
from etl.src.ontology import ontology_parser, ontology_updater
from pymongo import MongoClient

# Получаем логгер
log = logging.getLogger(__name__) # <--- ДОБАВЛЕНО: Получаем логгер

# --- Конфигурация DAG ---
DEFAULT_ONTOLOGY_GIT_REPO_PATH = Variable.get("ontology_git_repo_path", default_var="/opt/airflow/ontology") # ИЗМЕНЕНО: Путь из docker-compose.yml

MONGO_URI = Variable.get("mongo_uri_for_etl", default_var="mongodb://mongo:27017/")
MONGO_DB_NAME = Variable.get("mongo_db_name_for_etl", default_var="scb_db") # Используйте актуальное имя БД из вашего .env

# --- Python Callables для задач DAG ---

def parse_specific_ontology_version(**kwargs):
    """
    Парсит указанную версию онтологии из локального Git-репозитория.
    Ожидает 'ontology_version_to_sync' и 'ontology_git_path' в dag_run.conf.
    """
    ti = kwargs['ti']
    dag_run_conf = kwargs['dag_run'].conf
    
    # Получаем параметры из конфигурации запуска DAG или из params по умолчанию
    ontology_version_to_sync = dag_run_conf.get('ontology_version_to_sync')
    ontology_base_path = dag_run_conf.get('ontology_git_path')

    if not ontology_version_to_sync:
        raise ValueError("Parameter 'ontology_version_to_sync' not found in DAG run configuration or params.")
    if not ontology_base_path:
        raise ValueError("Parameter 'ontology_git_path' not found in DAG run configuration or params.")

    version_full_path = os.path.join(ontology_base_path, "versions", ontology_version_to_sync)

    log.info(f"Attempting to parse ontology version '{ontology_version_to_sync}' from path: {version_full_path}")
    
    version_id, schema_data, vocabularies_data = ontology_parser.parse_ontology_version_from_path(version_full_path)
    
    if not version_id or not schema_data:
        raise ValueError(f"Failed to parse schema for ontology version '{ontology_version_to_sync}' from {version_full_path}. Check logs.")

    ti.xcom_push(key="parsed_version_id", value=version_id)
    ti.xcom_push(key="parsed_schema_data", value=schema_data)
    ti.xcom_push(key="parsed_vocabularies_data", value=vocabularies_data or {}) # Передаем пустой dict если None
    log.info(f"Successfully parsed ontology version: {version_id}")


def upload_parsed_ontology_to_mongo(**kwargs):
    """
    Загружает распарсенную онтологию (Green-версию) в MongoDB.
    """
    ti = kwargs['ti']
    version_id = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_version_id")
    schema_data = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_schema_data")
    vocabularies_data = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_vocabularies_data")

    if not version_id or not schema_data:
        raise ValueError("Parsed ontology data not found in XComs. Previous task might have failed.")

    log.info(f"Attempting to upload ontology version '{version_id}' to MongoDB.")
    client = MongoClient(MONGO_URI)
    # db_client = client # ontology_updater ожидает MongoClient
    
    # Убедимся, что vocabularies_data это словарь
    vocab_data_to_send = vocabularies_data if isinstance(vocabularies_data, dict) else {}

    ontology_updater.upload_ontology_version( # Убрал success =, т.к. функция возвращает None или кидает Exception
        version_id=version_id,
        schema_data=schema_data,
        vocabularies_data=vocab_data_to_send,
        db_client=client, # Передаем MongoClient
        db_name=MONGO_DB_NAME
    )
    client.close()
    # if not success: # Если функция ничего не возвращает, эта проверка не нужна, ошибки обрабатываются через Exception
    #     raise RuntimeError(f"Failed to upload ontology version '{version_id}' to MongoDB.")
    log.info(f"Successfully uploaded ontology version '{version_id}' (Green version).")


def activate_ontology_version_in_mongo(**kwargs):
    """
    Активирует загруженную версию онтологии (Blue/Green switch).
    """
    ti = kwargs['ti']
    version_id = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_version_id")
    
    if not version_id:
        raise ValueError("Version ID not found in XComs for activation.")

    log.info(f"Attempting to set ontology version '{version_id}' as active in MongoDB.")
    client = MongoClient(MONGO_URI)
    # db_client = client
    
    ontology_updater.set_active_ontology_version( # Убрал success =
        version_id=version_id,
        db_client=client,
        db_name=MONGO_DB_NAME
    )
    client.close()
    # if not success:
    #     raise RuntimeError(f"Failed to set ontology version '{version_id}' as active in MongoDB.")
    log.info(f"Successfully set ontology version '{version_id}' as active (Blue version).")

# --- Определение DAG ---
with DAG(
    dag_id='ontology_sync_dag',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1), # Рекомендуется использовать фиксированную дату в прошлом
    catchup=False,
    tags=['ontology', 'system'],
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    },
    params={ # <--- ДОБАВЛЕНО: Определение параметров для UI
        "ontology_git_path": Param(
            DEFAULT_ONTOLOGY_GIT_REPO_PATH, # Используем значение из Variable как default
            type="string",
            description="Path to the ontology git repository clone (absolute path inside Airflow worker/scheduler)."
        ),
        "ontology_version_to_sync": Param(
            "v1.0", # Пример значения по умолчанию
            type="string",
            description="Version of the ontology to sync (e.g., 'v1.0'). Must be a subfolder in <ontology_git_path>/versions/."
        )
    },
    doc_md="""
    ### Ontology Synchronization DAG
    This DAG parses an ontology version from a specified Git path and uploads/activates it in MongoDB.
    It implements a Blue/Green like deployment for ontology versions.
    
    **Trigger with configuration (JSON):**
    ```json
    {
      "ontology_git_path": "/opt/airflow/ontology",
      "ontology_version_to_sync": "v1.0"
    }
    ```
    `ontology_git_path` defaults to the Airflow Variable `ontology_git_repo_path` or `""" + DEFAULT_ONTOLOGY_GIT_REPO_PATH + """`.
    `ontology_version_to_sync` defaults to `v1.0`.
    """
) as dag:

    parse_ontology_version_task = PythonOperator(
        task_id='parse_ontology_version_task',
        python_callable=parse_specific_ontology_version,
        # op_kwargs не нужны, так как параметры берутся из dag_run.conf, который доступен в kwargs['dag_run']
    )

    upload_green_version_task = PythonOperator(
        task_id='upload_green_version_task',
        python_callable=upload_parsed_ontology_to_mongo,
    )

    activate_blue_version_task = PythonOperator(
        task_id='activate_blue_version_task',
        python_callable=activate_ontology_version_in_mongo,
    )

    parse_ontology_version_task >> upload_green_version_task >> activate_blue_version_task