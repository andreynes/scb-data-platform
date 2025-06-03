# etl/src/transform/parsing/pdf_parser.py
import pdfplumber
import io
from typing import List, Dict, Any

def extract_tables_from_pdf(
    file_content: bytes, 
    pages: str = 'all' # или конкретные страницы '1', '1,3', '1-3'
) -> List[List[Dict[str, Any]]]: # Список таблиц, каждая таблица - список словарей-строк
    """
    Извлекает таблицы из PDF файла.
    Для MVP может извлекать только первую найденную таблицу.
    """
    all_tables_data: List[List[Dict[str, Any]]] = []
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            target_pages = []
            if pages == 'all':
                target_pages = pdf.pages
            else:
                # Простая логика разбора номеров страниц (можно усложнить)
                try:
                    page_indices = [int(p.strip()) - 1 for p in pages.split(',')]
                    target_pages = [pdf.pages[i] for i in page_indices if 0 <= i < len(pdf.pages)]
                except ValueError:
                     print(f"Invalid page numbers specified: {pages}")
                     return [] # или обработать ошибку иначе

            for page in target_pages:
                tables = page.extract_tables() # извлекает все таблицы со страницы
                for table in tables:
                    if not table: # Если таблица пуста
                        continue
                    # Первая строка таблицы используется как заголовки
                    headers = [str(header) if header is not None else f"column_{i}" for i, header in enumerate(table[0])]
                    table_data: List[Dict[str, Any]] = []
                    for row in table[1:]: # Пропускаем заголовки
                        row_dict = {}
                        for i, cell in enumerate(row):
                            row_dict[headers[i]] = str(cell) if cell is not None else None
                        table_data.append(row_dict)
                    if table_data:
                        all_tables_data.append(table_data)
        
        # Для MVP возвращаем только первую таблицу, если она есть
        # return all_tables_data[0] if all_tables_data else []
        # Или все таблицы, если нужно
        return all_tables_data

    except Exception as e:
        print(f"Error parsing PDF file: {e}")
        return []