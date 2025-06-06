from __future__ import annotations

import pendulum
import sys
import os
from airflow.decorators import dag, task

@dag(
    dag_id='test_pythonpath',
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=['debug'],
)
def test_pythonpath_pipeline():
    @task
    def print_sys_path_and_env():
        print("sys.path:")
        for p in sys.path:
            print(f"  - {p}")
        print("\nPYTHONPATH environment variable:")
        print(f"  PYTHONPATH = {os.getenv('PYTHONPATH')}")
        
        try:
            import pydantic_settings
            print("\nSuccessfully imported pydantic_settings")
        except ModuleNotFoundError as e:
            print(f"\nFailed to import pydantic_settings: {e}")

        try:
            import pymongo
            print("\nSuccessfully imported pymongo")
        except ModuleNotFoundError as e:
            print(f"\nFailed to import pymongo: {e}")

    print_sys_path_and_env()

test_pythonpath_dag_instance = test_pythonpath_pipeline()