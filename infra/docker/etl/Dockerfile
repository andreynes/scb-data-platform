# Используем официальный образ Airflow как базовый
ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Устанавливаем рабочую директорию Airflow
WORKDIR /opt/airflow

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем файл зависимостей ETL
COPY ./etl/requirements.txt /requirements.txt

# Важно: Устанавливаем зависимости от пользователя airflow
# Базовый образ Airflow уже настроен на пользователя airflow
# Если бы требовались системные пакеты (apt-get), то сначала USER root, потом USER airflow
USER airflow 
RUN pip install --user --no-cache-dir -r /requirements.txt

# Копируем исходный код ETL (наши модули)
# Эти файлы будут импортироваться в DAG'ах
# Убедимся, что airflow имеет права на эти папки после копирования
# Копируем от имени текущего пользователя (airflow)
COPY --chown=airflow:airflow ./etl/src /opt/airflow/etl_src

# Копируем DAG'и
COPY --chown=airflow:airflow ./etl/dags /opt/airflow/dags

# Копируем папку онтологии
COPY --chown=airflow:airflow ./ontology /opt/airflow/ontology_repo_local_clone

# Возвращаемся к root, если нужно для каких-то дальнейших команд, но обычно не требуется
# USER root 
# Если больше команд нет, можно оставить USER airflow