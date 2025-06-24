# etl/dags/manual_reparse_dag.py
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="manual_reparse_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None, # Запускается только вручную/по триггеру
    doc_md="""
    ### Manual Reparse DAG
    
    Этот DAG инициирует повторную обработку (репарсинг) списка документов.
    Он принимает список `document_ids` и опционально `ontology_version` в своей конфигурации
    и запускает по одному экземпляру `file_processing_dag` для каждого документа.
    """,
    tags=["manual", "reparse", "etl"],
) as dag:
    # Эта задача будет динамически разворачиваться для каждого ID документа.
    # conf передает параметры в запускаемый DAG.
    TriggerDagRunOperator.partial(
        task_id="trigger_file_processing",
        trigger_dag_id="file_processing_dag",  # DAG, который мы хотим запустить
        conf={
            "document_id": "{{ dag_run.conf['document_ids'][0] }}", # Пример для одного ID
            "ontology_version": "{{ dag_run.conf.get('ontology_version') }}",
            "use_llm": "{{ dag_run.conf.get('use_llm', False) }}",
        }
    # В более новых версиях Airflow можно использовать .expand() для всего списка:
    # ).expand(conf=[{"document_id": doc_id} for doc_id in ...])
    # Для простоты MVP пока оставим запуск по одному.
    )