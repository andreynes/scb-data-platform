# etl/src/transform/parsing/llm_parser.py
import json
from typing import List, Dict, Any
from etl.src.llm.llm_client import LLMClient
from etl.src.llm import prompt_formatter

async def parse_with_llm(
    input_data: Dict,
    ontology_schema: Dict[str, Any],
    llm_client: LLMClient
) -> List[Dict[str, Any]]:
    """Использует LLM для парсинга данных."""
    input_json_str = json.dumps(input_data, ensure_ascii=False, indent=2)

    instructions = "Извлеки данные и верни результат в виде списка JSON-объектов. Каждый объект должен соответствовать одному атому данных."
    prompt = prompt_formatter.format_data_extraction_prompt(
        input_data_str=input_json_str,
        ontology_schema=ontology_schema,
        extraction_instructions=instructions
    )

    response_str = await llm_client.send_request_to_llm(prompt)

    # Пытаемся извлечь JSON из ответа
    try:
        # Простая очистка ответа, может потребовать улучшения
        json_str = response_str.strip().strip('```json').strip('```')
        parsed_data = json.loads(json_str)
        if isinstance(parsed_data, list):
            return parsed_data
        else:
            # Если LLM вернул один объект вместо списка
            return [parsed_data]
    except json.JSONDecodeError:
        # TODO: Можно попробовать попросить LLM исправить JSON
        print(f"Failed to decode JSON from LLM response: {response_str}")
        return []