import sys
import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.models.param import Param

# Убираем sys.path.append, так как это будет настроено в docker-compose.yml

# ИСПРАВЛЕННЫЕ ИМПОРТЫ
from src.ontology import ontology_parser, ontology_updater
from pymongo import MongoClient

log = logging.getLogger(__name__)

# --- Конфигурация DAG ---
DEFAULT_ONTOLOGY_GIT_REPO_PATH = Variable.get("ontology_git_repo_path", default_var="/opt/airflow/ontology")
MONGO_URI = Variable.get("mongo_uri_for_etl", default_var="mongodb://mongo:27017/")
MONGO_DB_NAME = Variable.get("mongo_db_name_for_etl", default_var="scb_db")

# --- Python Callables ---

def parse_specific_ontology_version(**kwargs):
    ti = kwargs['ti']
    dag_run_conf = kwargs['dag_run'].conf
    ontology_version_to_sync = dag_run_conf.get('ontology_version_to_sync')
    ontology_base_path = dag_run_conf.get('ontology_git_path')

    if not ontology_version_to_sync or not ontology_base_path:
        raise ValueError("Parameters 'ontology_version_to_sync' and 'ontology_git_path' are required.")

    version_full_path = os.path.join(ontology_base_path, "versions", ontology_version_to_sync)
    log.info(f"Parsing ontology version '{ontology_version_to_sync}' from path: {version_full_path}")
    
    version_id, schema_data, vocabularies_data = ontology_parser.parse_ontology_version_from_path(version_full_path)
    
    if not version_id or not schema_data:
        raise ValueError(f"Failed to parse schema for ontology version '{ontology_version_to_sync}'.")

    ti.xcom_push(key="parsed_version_id", value=version_id)
    ti.xcom_push(key="parsed_schema_data", value=schema_data)
    ti.xcom_push(key="parsed_vocabularies_data", value=vocabularies_data or {})
    log.info(f"Successfully parsed ontology version: {version_id}")

def upload_parsed_ontology_to_mongo(**kwargs):
    ti = kwargs['ti']
    version_id = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_version_id")
    schema_data = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_schema_data")
    vocabularies_data = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_vocabularies_data")

    if not version_id or not schema_data:
        raise ValueError("Parsed ontology data not found in XComs.")

    log.info(f"Uploading ontology version '{version_id}' to MongoDB.")
    client = MongoClient(MONGO_URI)
    
    ontology_updater.upload_ontology_version(
        version_id=version_id,
        schema_data=schema_data,
        vocabularies_data=vocabularies_data,
        db_client=client,
        db_name=MONGO_DB_NAME
    )
    client.close()
    log.info(f"Successfully uploaded ontology version '{version_id}'.")

def activate_ontology_version_in_mongo(**kwargs):
    ti = kwargs['ti']
    version_id = ti.xcom_pull(task_ids="parse_ontology_version_task", key="parsed_version_id")
    
    if not version_id:
        raise ValueError("Version ID not found in XComs.")

    log.info(f"Setting ontology version '{version_id}' as active.")
    client = MongoClient(MONGO_URI)
    
    ontology_updater.set_active_ontology_version(
        version_id=version_id,
        db_client=client,
        db_name=MONGO_DB_NAME
    )
    client.close()
    log.info(f"Successfully activated ontology version '{version_id}'.")

# --- Определение DAG ---
with DAG(
    dag_id='ontology_sync_dag',
    schedule=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ontology', 'system'],
    params={
        "ontology_git_path": Param(DEFAULT_ONTOLOGY_GIT_REPO_PATH, type="string"),
        "ontology_version_to_sync": Param("v1.0", type="string"),
    },
) as dag:
    parse_task = PythonOperator(task_id='parse_ontology_version_task', python_callable=parse_specific_ontology_version)
    upload_task = PythonOperator(task_id='upload_green_version_task', python_callable=upload_parsed_ontology_to_mongo)
    activate_task = PythonOperator(task_id='activate_blue_version_task', python_callable=activate_ontology_version_in_mongo)

    parse_task >> upload_task >> activate_task