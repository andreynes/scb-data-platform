# etl/src/llm/prompt_formatter.py
from typing import Dict, Any, List

def _format_ontology_for_prompt(ontology_schema: Dict[str, Any]) -> str:
    """Преобразует схему онтологии в строку для промпта."""
    attributes_str = "\n".join(
        f"- {attr.get('name')}: {attr.get('description')} (type: {attr.get('type')})"
        for attr in ontology_schema.get('attributes', [])
    )
    return f"Целевая схема данных (атрибуты):\n{attributes_str}"

def format_data_extraction_prompt(
    input_data_str: str,
    ontology_schema: Dict[str, Any],
    extraction_instructions: str
) -> str:
    """Формирует полный промпт для извлечения данных."""
    ontology_str = _format_ontology_for_prompt(ontology_schema)

    prompt = f"""
    Проанализируй следующие входные данные и извлеки информацию согласно указанной целевой схеме.

    {ontology_str}

    Входные данные:
    ---
    {input_data_str[:8000]}
    ---

    Инструкции по извлечению:
    {extraction_instructions}
    """
    return prompt.strip()