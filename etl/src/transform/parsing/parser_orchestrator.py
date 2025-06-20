# etl/src/transform/parsing/parser_orchestrator.py
from typing import List, Dict, Any, Optional
import json

# Импортируем все наши парсеры и утилиты
from .excel_parser import parse_excel_data
from .pdf_parser import extract_tables_from_pdf
from .llm_parser import parse_with_llm  # <-- ДОБАВЛЕНО: Импорт LLM парсера

# Импортируем LLM клиент, чтобы передавать его тип
from etl.src.llm.llm_client import LLMClient 

# Импортируем логгер
from ...utils.logging_utils import setup_etl_logger

logger = setup_etl_logger(__name__)


def _get_first_table_from_json_dict(json_data: Dict[str, Any], doc_id: str) -> Optional[List[Dict[str, Any]]]:
    """Вспомогательная функция для извлечения первой таблицы из словаря."""
    for sheet_name, sheet_data in json_data.items():
        if isinstance(sheet_data, list) and all(isinstance(item, dict) for item in sheet_data):
            logger.info(f"Using sheet '{sheet_name}' from JSON representation for doc_id: {doc_id}.")
            return sheet_data
    logger.warning(f"Could not find a list of dicts (table) within the JSON representation dict for doc_id: {doc_id}.")
    return None

# --- ОБНОВЛЕННАЯ ФУНКЦИЯ ---
async def parse_document_content(
    document_metadata: Dict[str, Any],
    ontology_schema: Dict[str, Any],
    # file_content нам пока не нужен, т.к. мы работаем с JSON представлением
    # file_content: Optional[bytes] = None, 
    # Добавляем параметры для LLM
    use_llm: bool = False,
    llm_client: Optional[LLMClient] = None
) -> List[Dict[str, Any]]:
    """
    Оркестрирует парсинг документа.
    
    1. Если use_llm=True, вызывает LLM-парсер.
    2. Иначе, пытается использовать готовое JSON-представление.
    3. (В будущем) Если ничего не сработало, может парсить сырой файл.
    """
    doc_id = document_metadata.get('_id', 'unknown_id')
    json_data = document_metadata.get('json_representation')

    if not json_data:
        logger.warning(f"No JSON representation found for document_id: {doc_id}. Cannot parse.")
        return []

    # --- СТРАТЕГИЯ 1: ИСПОЛЬЗОВАНИЕ LLM (если указано) ---
    if use_llm:
        if not llm_client:
            logger.error("LLMClient is required for LLM parsing but was not provided.")
            raise ValueError("LLMClient is required when use_llm is True")
        
        logger.info(f"Attempting to parse document {doc_id} with LLM.")
        return await llm_parser.parse_with_llm(
            input_data=json_data,
            ontology_schema=ontology_schema,
            llm_client=llm_client
        )
    
    # --- СТРАТЕГИЯ 2: Использование готового JSON (поведение по умолчанию) ---
    logger.info(f"Using pre-existing JSON representation for document {doc_id}.")
    
    # Предполагаем, что корректный формат - это список словарей
    if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
        return json_data
    
    # Если это словарь (например, разные листы Excel), пытаемся найти первую таблицу
    if isinstance(json_data, dict):
        result = _get_first_table_from_json_dict(json_data, doc_id)
        return result if result is not None else []

    logger.warning(f"JSON representation for doc_id {doc_id} has an unsupported format: {type(json_data)}")
    return []

    # --- СТРАТЕГИЯ 3: (Будущее) Парсинг сырого файла, если первые два не сработали ---
    # ... здесь будет логика вызова excel_parser / pdf_parser напрямую с file_content ...


if __name__ == '__main__':
    # Пример использования (теперь требует асинхронного запуска)
    import asyncio

    # Пример 1: JSON уже есть, используем его напрямую (use_llm=False)
    mock_meta_with_json = {
        "_id": "doc1",
        "json_representation": [
            {"Колонка1": "Значение1", "Колонка2": 10},
            {"Колонка1": "Значение2", "Колонка2": 20}
        ]
    }
    
    # Мок схемы онтологии, необходим для LLM
    mock_ontology = {
        "attributes": [
            {"name": "col_1", "description": "Первая колонка"},
            {"name": "col_2", "description": "Вторая колонка"}
        ]
    }
    
    async def main_test():
        print("--- Testing with pre-existing JSON ---")
        result_json = await parse_document_content(
            mock_meta_with_json, 
            mock_ontology, 
            use_llm=False
        )
        print(f"Result: {result_json}\n")

        # Пример 2: Использование LLM
        # Для этого теста нужно создать мок LLMClient
        class MockLLMClient:
            async def send_request_to_llm(self, prompt: str, **kwargs) -> str:
                print("\n--- LLM Prompt ---")
                print(prompt)
                print("------------------")
                # Имитируем ответ LLM в формате JSON
                return '[{"col_1": "ParsedValue1", "col_2": 100}]'

        print("--- Testing with LLM ---")
        result_llm = await parse_document_content(
            mock_meta_with_json,
            mock_ontology,
            use_llm=True,
            llm_client=MockLLMClient()
        )
        print(f"Result: {result_llm}")

    asyncio.run(main_test())