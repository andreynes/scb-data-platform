import json
import asyncio
from typing import List, Dict, Any, Optional

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
# Импортируем только самые базовые парсеры и клиенты.
# Логика вызова перенесена в этот файл.
from etl.src.transform.parsing.excel_parser import parse_excel_data
from etl.src.transform.parsing.pdf_parser import extract_tables_from_pdf
from etl.src.llm.llm_client import LLMClient
from etl.src.llm import prompt_formatter
from etl.src.utils.logging_utils import setup_etl_logger
# --------------------------------

logger = setup_etl_logger(__name__)


async def _parse_with_llm(
    input_data: Dict,
    ontology_schema: Dict[str, Any],
    llm_client: LLMClient
) -> List[Dict[str, Any]]:
    """
    Приватная функция для формирования промпта, вызова LLM и парсинга ответа.
    Эта логика теперь является частью оркестратора.
    """
    input_json_str = json.dumps(input_data, ensure_ascii=False, indent=2)

    instructions = "Извлеки данные и верни результат в виде списка JSON-объектов. Каждый объект должен соответствовать одному атому данных."
    prompt = prompt_formatter.format_data_extraction_prompt(
        input_data_str=input_json_str,
        ontology_schema=ontology_schema,
        extraction_instructions=instructions
    )

    logger.info("Sending request to LLM for data extraction...")
    response_str = await llm_client.send_request_to_llm(prompt)

    try:
        # Пытаемся извлечь JSON из ответа
        logger.debug(f"LLM response received: {response_str}")
        json_str = response_str.strip().strip('```json').strip('```')
        parsed_data = json.loads(json_str)
        if isinstance(parsed_data, list):
            return parsed_data
        elif isinstance(parsed_data, dict):
            # Если LLM вернул один объект вместо списка
            return [parsed_data]
        else:
            logger.warning(f"LLM returned data in an unexpected format (not a list or dict): {type(parsed_data)}")
            return []
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from LLM response: {response_str}")
        # TODO: Можно попробовать попросить LLM исправить JSON
        return []


def _get_first_table_from_json_dict(json_data: Dict[str, Any], doc_id: str) -> Optional[List[Dict[str, Any]]]:
    """Вспомогательная функция для извлечения первой таблицы из словаря."""
    for sheet_name, sheet_data in json_data.items():
        if isinstance(sheet_data, list) and all(isinstance(item, dict) for item in sheet_data):
            logger.info(f"Using sheet '{sheet_name}' from JSON representation for doc_id: {doc_id}.")
            return sheet_data
    logger.warning(f"Could not find a list of dicts (table) within the JSON representation dict for doc_id: {doc_id}.")
    return None


async def parse_document_content(
    document_metadata: Dict[str, Any],
    ontology_schema: Dict[str, Any],
    use_llm: bool = False,
    llm_client: Optional[LLMClient] = None,
    file_content: Optional[bytes] = None # Добавили обратно, для будущих стратегий
) -> List[Dict[str, Any]]:
    """
    Оркестрирует парсинг документа, выбирая подходящую стратегию.
    """
    doc_id = document_metadata.get('_id', 'unknown_id')
    
    # --- СТРАТЕГИЯ 1: Принудительное использование LLM ---
    if use_llm:
        if not llm_client:
            raise ValueError("LLMClient is required when use_llm is True")
        
        json_data_for_llm = document_metadata.get('json_representation')
        if not json_data_for_llm:
            logger.warning(f"No JSON representation for LLM parsing for doc_id: {doc_id}. Cannot parse.")
            return []
            
        logger.info(f"Attempting to parse document {doc_id} with LLM (forced).")
        return await _parse_with_llm(
            input_data=json_data_for_llm,
            ontology_schema=ontology_schema,
            llm_client=llm_client
        )

    # --- СТРАТЕГИЯ 2: Использование готового JSON-представления ---
    json_data = document_metadata.get('json_representation')
    if json_data:
        logger.info(f"Using pre-existing JSON representation for document {doc_id}.")
        
        if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
            return json_data
        
        if isinstance(json_data, dict):
            result = _get_first_table_from_json_dict(json_data, doc_id)
            return result if result is not None else []
        
        logger.warning(f"JSON representation for doc_id {doc_id} has an unsupported format: {type(json_data)}")

    # Если дошли сюда, значит, первые стратегии не сработали
    logger.warning(f"No valid parsing strategy found for document {doc_id} with current inputs.")
    return []


# Блок для локального тестирования
if __name__ == '__main__':
    mock_meta_with_json = {
        "_id": "doc1",
        "json_representation": {
            "Sheet1": [
                {"Колонка1": "Значение1", "Колонка2": 10},
                {"Колонка1": "Значение2", "Колонка2": 20}
            ]
        }
    }
    
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

        class MockLLMClient:
            async def send_request_to_llm(self, prompt: str, **kwargs) -> str:
                print("\n--- LLM Prompt ---")
                print(prompt)
                print("------------------")
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