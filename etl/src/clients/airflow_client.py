# etl/src/clients/airflow_client.py

import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


async def trigger_dag(
    dag_id: str,
    conf: Optional[Dict[str, Any]] = None,
    airflow_api_url: str = "http://airflow-webserver:8080/api/v1",
    auth: Optional[tuple[str, str]] = ("airflow", "airflow"),
) -> bool:
    """
    Triggers a DAG run in Airflow via its REST API.

    Args:
        dag_id: The ID of the DAG to trigger.
        conf: A configuration dictionary for the DAG run.
        airflow_api_url: The base URL of the Airflow API.
        auth: A tuple of (username, password) for Airflow basic authentication.

    Returns:
        True if the DAG was triggered successfully, False otherwise.
    """
    endpoint = f"{airflow_api_url}/dags/{dag_id}/dagRuns"
    payload = {"conf": conf or {}}

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Triggering DAG '{dag_id}' with conf: {conf}")
            response = await client.post(endpoint, json=payload, auth=auth)

            response.raise_for_status()  # Will raise an exception for 4xx/5xx status codes

            logger.info(
                f"Successfully triggered DAG '{dag_id}'. "
                f"Airflow API response: {response.json()}"
            )
            return True

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Failed to trigger DAG '{dag_id}'. "
            f"HTTP Status: {e.response.status_code}. Response: {e.response.text}"
        )
        return False
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Airflow API at '{endpoint}'. Error: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while triggering DAG '{dag_id}': {e}", exc_info=True)
        return False