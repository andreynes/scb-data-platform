# backend/app/clients/airflow_client.py

import httpx
import logging
from typing import Dict, Any, Optional

from core.config import settings

logger = logging.getLogger(__name__)

async def trigger_dag(
    dag_id: str,
    conf: Dict[str, Any],
    airflow_url: Optional[str] = settings.AIRFLOW_API_URL,
    auth: Optional[tuple] = (settings.AIRFLOW_API_USER, settings.AIRFLOW_API_PASSWORD)
) -> bool:
    """
    Инициирует запуск DAG в Airflow через REST API.
    """
    if not airflow_url or not auth or not auth[0] or not auth[1]:
        logger.error("Airflow API is not configured. Cannot trigger DAG. Check AIRFLOW_API_URL, AIRFLOW_API_USER, AIRFLOW_API_PASSWORD.")
        return False

    api_endpoint = f"{airflow_url.rstrip('/')}/api/v1/dags/{dag_id}/dagRuns"
    
    payload = {
        "conf": conf
    }

    try:
        async with httpx.AsyncClient(auth=auth) as client:
            response = await client.post(api_endpoint, json=payload, timeout=10.0)
            response.raise_for_status()
            
            logger.info(f"Successfully triggered DAG '{dag_id}' for document '{conf.get('document_id')}'. Response: {response.json()}")
            return True
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Failed to trigger DAG '{dag_id}'. "
            f"Status: {e.response.status_code}. Response: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Network error while trying to trigger DAG '{dag_id}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in trigger_dag: {e}", exc_info=True)
        
    return False