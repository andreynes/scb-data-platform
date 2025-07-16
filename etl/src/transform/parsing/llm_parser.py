# etl/src/transform/parsing/llm_parser.py
import json
from typing import List, Dict, Any

from src.llm.llm_client import LLMClient
from src.llm import prompt_formatter

# Эта функция теперь будет частью оркестратора
# async def parse_with_llm(...) ...