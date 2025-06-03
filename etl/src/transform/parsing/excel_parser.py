# etl/src/transform/parsing/excel_parser.py
import pandas as pd
import io
from typing import List, Dict, Any, Optional

def parse_excel_data(
    file_content: bytes, 
    sheet_name: Optional[str] = 0, # 0 для первого листа
    header_row: Optional[int] = 0   # 0 для первой строки как заголовка
) -> List[Dict[str, Any]]:
    """
    Парсит данные из Excel файла.
    Возвращает список словарей, где каждый словарь - строка таблицы.
    """
    try:
        df = pd.read_excel(
            io.BytesIO(file_content), 
            sheet_name=sheet_name, 
            header=header_row
        )
        # Преобразуем NaN в None для совместимости с JSON и др.
        df = df.where(pd.notnull(df), None) 
        return df.to_dict(orient='records')
    except Exception as e:
        # Здесь можно использовать ваш логгер
        print(f"Error parsing Excel file: {e}")
        return []