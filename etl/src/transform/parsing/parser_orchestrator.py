# etl/src/transform/parsing/parser_orchestrator.py
from typing import List, Dict, Any, Optional, Union
from ..extract.mongo_extractor import get_json_representation_from_metadata # Для получения JSON из метаданных
# Предполагаем, что get_original_file_content (если файлы не в JSON) будет в file_extractor
# from ..extract.file_extractor import get_original_file_content 
from .excel_parser import parse_excel_data
from .pdf_parser import extract_tables_from_pdf 
# Импортируем ваш логгер
from ...utils.logging_utils import setup_etl_logger

logger = setup_etl_logger(__name__)

def parse_document_content(
    document_metadata: Dict[str, Any],
    # file_content: Optional[bytes], # Это если мы читаем байты файла напрямую
    # ontology_schema: Dict[str, Any] # Пока не используем, но может понадобиться для более умного парсинга
) -> List[Dict[str, Any]]: # Возвращаем список словарей (одна таблица для MVP)
    """
    Оркестрирует парсинг документа на основе его метаданных.
    Для MVP просто выбирает парсер по типу файла или использует готовый JSON.
    """
    
    content_type = document_metadata.get('content_type')
    filename = document_metadata.get('filename', '') # Получаем имя файла для расширения

    # Стратегия 1: Если JSON представление уже есть в метаданных (например, после OCR или другого процесса)
    # Для MVP, будем считать, что если JSON есть, то это уже распарсенные данные в нужном формате.
    # В будущем здесь может быть логика, которая понимает, что этот JSON еще нужно "допарсить".
    json_data = get_json_representation_from_metadata(document_metadata)
    if json_data:
        logger.info(f"Using pre-existing JSON representation for document_id: {document_metadata.get('_id')}")
        # Для MVP предполагаем, что json_data это уже List[Dict[str, Any]] или Dict, который можно так вернуть
        # Если json_data - это словарь, представляющий ОДНУ таблицу (листы Excel/страницы PDF), 
        # то нужно выбрать, какую часть брать.
        # Для MVP, если это словарь, просто вернем его как единственный элемент списка
        if isinstance(json_data, dict): # Простой случай, если JSON это уже одна "таблица"
            # Если наш excel_parser/pdf_parser возвращают список словарей,
            # то и здесь должен быть такой же формат - List[Dict[str,Any]]
            # Если JSON это { "Sheet1": [...], "Sheet2": [...] }, нужно выбрать один лист
            # Пока сделаем очень просто: если это словарь, ожидаем, что это и есть наши данные
            # или это одна таблица, которую мы оборачиваем в список
            # Эта логика будет зависеть от того, как JSON представление сохраняется.
            # Для MVP предположим, что если json_data есть, то это уже готовый List[Dict]
            if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                return json_data
            elif isinstance(json_data, dict): # Например, один лист Excel сохранен как словарь
                 # Эта логика упрощена. Реально нужно будет смотреть структуру json_data
                logger.warning(f"JSON representation is a dict, attempting to use its values if they form a table for doc_id: {document_metadata.get('_id')}")
                # Попытка извлечь первую таблицу из словаря словарей/списков
                for sheet_name, sheet_data in json_data.items():
                    if isinstance(sheet_data, list) and all(isinstance(item, dict) for item in sheet_data):
                        logger.info(f"Using sheet '{sheet_name}' from JSON representation.")
                        return sheet_data # Возвращаем первую подходящую "таблицу"
                logger.warning("Could not find a list of dicts within the JSON representation dict.")
                return [] 
        else:
            logger.warning(f"JSON representation is not a list of dicts or a dict for doc_id: {document_metadata.get('_id')}. Type: {type(json_data)}")
            return []


    # Стратегия 2: Если JSON нет, пытаемся парсить оригинальный файл (если он есть)
    # Для этого нам нужен file_content. В MVP мы пока не передаем file_content напрямую,
    # а предполагаем, что JSON представление должно было быть создано ранее (например, при загрузке).
    # Этот блок пока оставляем как заглушку для будущих улучшений или если изменим подход.
    #
    # file_content_bytes = ... # Здесь нужно получить file_content_bytes, например, из GridFS или S3,
    #                       # используя original_file_ref из document_metadata
    #
    # if file_content_bytes:
    #     logger.info(f"Parsing original file content for document_id: {document_metadata.get('_id')}")
    #     if 'excel' in content_type or filename.endswith(('.xls', '.xlsx')):
    #         logger.info("Detected Excel file, using excel_parser.")
    #         # parse_excel_data ожидает байты
    #         parsed_tables = parse_excel_data(file_content_bytes) 
    #         return parsed_tables # parse_excel_data уже возвращает List[Dict[str, Any]] для первого листа
    #     elif 'pdf' in content_type or filename.endswith('.pdf'):
    #         logger.info("Detected PDF file, using pdf_parser.")
    #         # extract_tables_from_pdf ожидает байты и возвращает List[List[Dict[str, Any]]]
    #         parsed_tables_list = extract_tables_from_pdf(file_content_bytes)
    #         if parsed_tables_list: # Для MVP берем первую таблицу
    #             return parsed_tables_list[0] 
    #         return []
    #     else:
    #         logger.warning(f"Unsupported content_type '{content_type}' or filename '{filename}' for parsing original file.")
    #         return []
    # else:
    #     logger.warning(f"No JSON representation and no original file content found/provided for document_id: {document_metadata.get('_id')}")
    #     return []

    logger.warning(f"No JSON representation found for document_id: {document_metadata.get('_id')}. Cannot parse.")
    return []


if __name__ == '__main__':
    # Пример использования (требует моков или реальных данных в MongoDB)
    # Для простого теста можно создать мок document_metadata
    
    # Пример 1: JSON уже есть
    mock_meta_with_json = {
        "_id": "doc1",
        "filename": "test.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "json_representation": [ # Предполагаем, что JSON это уже List[Dict]
            {"Колонка1": "Значение1", "Колонка2": 10},
            {"Колонка1": "Значение2", "Колонка2": 20}
        ]
    }
    print("--- Testing with pre-existing JSON ---")
    result_json = parse_document_content(mock_meta_with_json)
    print(f"Result: {result_json}")

    # Пример 2: JSON нет (этот сценарий пока не будет работать без file_content)
    mock_meta_no_json = {
        "_id": "doc2",
        "filename": "another.pdf",
        "content_type": "application/pdf",
        # "original_file_ref_gridfs_id": "some_gridfs_id" # для сценария с чтением файла
    }
    print("\n--- Testing without JSON (MVP: expects pre-parsed JSON or error) ---")
    result_no_json = parse_document_content(mock_meta_no_json)
    print(f"Result: {result_no_json}") # Ожидаем пустой список или лог с предупреждением