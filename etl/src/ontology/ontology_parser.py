import yaml
import os
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def parse_ontology_version_from_path(version_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[Dict[str, List[Any]]]]:
    """
    Парсит все файлы YAML для указанной версии онтологии из файловой системы.

    Args:
        version_path: Абсолютный или относительный путь к директории версии онтологии
                      (например, /opt/airflow/ontology/versions/v1.0).

    Returns:
        Кортеж (version_id, schema_data, vocabularies_data).
        version_id: Строка ID версии (например, "v1.0").
        schema_data: Словарь с данными из schema.yaml.
        vocabularies_data: Словарь, где ключ - имя справочника,
                           а значение - список его элементов.
        Возвращает (None, None, None) в случае критической ошибки.
    """
    logger.info(f"Parsing ontology from path: {version_path}")

    schema_file_path = os.path.join(version_path, "schema.yaml")
    vocabularies_dir_path = os.path.join(version_path, "vocabularies")

    schema_data: Optional[Dict[str, Any]] = None
    version_id: Optional[str] = None

    # 1. Парсинг schema.yaml
    if not os.path.exists(schema_file_path):
        logger.error(f"Schema file not found: {schema_file_path}")
        return None, None, None

    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            schema_data = yaml.safe_load(f)
        if schema_data and isinstance(schema_data, dict) and "version" in schema_data:
            version_id = str(schema_data["version"])
            logger.info(f"Parsed schema.yaml for version: {version_id}")
        else:
            logger.error(f"Invalid schema.yaml: 'version' key not found or file is not a dictionary in {schema_file_path}")
            return None, None, None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing schema.yaml: {e}")
        return None, None, None
    except IOError as e:
        logger.error(f"Error reading schema.yaml: {e}")
        return None, None, None

    # 2. Парсинг справочников из папки vocabularies/
    vocabularies_data: Dict[str, List[Any]] = {}
    if os.path.isdir(vocabularies_dir_path):
        try:
            for filename in os.listdir(vocabularies_dir_path):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    vocab_name = os.path.splitext(filename)[0]
                    vocab_file_path = os.path.join(vocabularies_dir_path, filename)
                    try:
                        with open(vocab_file_path, 'r', encoding='utf-8') as vf:
                            vocab_content = yaml.safe_load(vf)
                        if isinstance(vocab_content, list):
                            vocabularies_data[vocab_name] = vocab_content
                            logger.debug(f"Parsed vocabulary: {vocab_name} from {filename}")
                        else:
                            logger.warning(f"Vocabulary file {filename} does not contain a list. Skipping.")
                    except yaml.YAMLError as e_voc:
                        logger.warning(f"Error parsing vocabulary file {filename}: {e_voc}. Skipping.")
                    except IOError as e_voc_io:
                        logger.warning(f"Error reading vocabulary file {filename}: {e_voc_io}. Skipping.")
        except OSError as e_dir:
             logger.warning(f"Error listing vocabularies directory {vocabularies_dir_path}: {e_dir}. No vocabularies will be loaded.")
    else:
        logger.info(f"Vocabularies directory not found: {vocabularies_dir_path}. No vocabularies will be loaded.")

    return version_id, schema_data, vocabularies_data

# Пример использования (для локального тестирования, если нужно)
if __name__ == '__main__':
    # Предполагается, что скрипт запускается из папки etl/src/ontology/
    # и онтология v1.0 находится в ../../../ontology/versions/v1.0/
    # Для реального тестирования путь должен быть корректным относительно места запуска.
    # Этот путь НЕ будет работать в Airflow DAG напрямую.
    example_path = "../../../ontology/versions/v1.0" # Относительно текущего файла
    
    # Настроим базовое логирование для вывода в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if os.path.exists(example_path) and os.path.isdir(example_path):
        v_id, s_data, voc_data = parse_ontology_version_from_path(example_path)
        if v_id:
            logger.info(f"Successfully parsed version: {v_id}")
            logger.info(f"Schema data keys: {list(s_data.keys()) if s_data else None}")
            logger.info(f"Loaded vocabularies: {list(voc_data.keys()) if voc_data else None}")
            if 'countries' in voc_data:
                logger.info(f"First 3 countries: {voc_data['countries'][:3] if voc_data['countries'] else 'N/A'}")
        else:
            logger.error("Failed to parse ontology.")
    else:
        logger.error(f"Example path for ontology not found or not a directory: {os.path.abspath(example_path)}")
        logger.error("Please ensure the ontology files are correctly placed relative to the script for this example to run.")
        logger.error("Current working directory: " + os.getcwd())