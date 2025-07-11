# etl/src/transform/parsing/parser_orchestrator.py
import json
from typing import List, Dict, Any, Optional

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
from .excel_parser import parse_excel_data
from .pdf_parser import extract_tables_from_pdf
from src.utils.logging_utils import setup_etl_logger
# --------------------------------

logger = setup_etl_logger(__name__)

def _get_first_table_from_json_dict(json_data: Dict[str, Any], doc_id: str) -> Optional[List[Dict[str, Any]]]:
    """Вспомогательная функция для извлечения первой таблицы из словаря."""
    for sheet_name, sheet_data in json_data.items():
        if isinstance(sheet_data, list) and all(isinstance(item, dict) for item in sheet_data):
            logger.info(f"Using sheet '{sheet_name}' from JSON representation for doc_id: {doc_id}.")
            return sheet_data
    logger.warning(f"Could not find a list of dicts (table) within the JSON representation dict for doc_id: {doc_id}.")
    return None

def parse_document_content(
    document_metadata: Dict[str, Any],
    ontology_schema: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Оркестрирует парсинг документа на основе имеющихся данных.
    Для MVP не использует LLM, а полагается на pre-parsed JSON.
    """
    doc_id = document_metadata.get('_id', 'unknown_id')

    # --- Основная стратегия: Использование готового JSON-представления ---
    json_data = document_metadata.get('json_representation')
    if json_data:
        logger.info(f"Using pre-existing JSON representation for document {doc_id}.")
        
        # Если JSON - это уже готовый список таблиц (атомов)
        if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
            return json_data
        
        # Если JSON - это словарь (например, { "Sheet1": [...] })
        if isinstance(json_data, dict):
            result = _get_first_table_from_json_dict(json_data, doc_id)
            return result if result is not None else []
        
        logger.warning(f"JSON representation for doc_id {doc_id} has an unsupported format: {type(json_data)}")

    # --- Запасная стратегия (если нет JSON-представления, но есть файл) ---
    # file_content = # ... здесь нужна логика получения file_content, если она будет ...
    # ... на основе document_metadata['content_type'] вызываем parse_excel_data и т.д.
    # В MVP это не реализуем, т.к. json_representation обязателен.

    logger.warning(f"No valid parsing strategy found for document {doc_id}. No JSON representation available.")
    return []