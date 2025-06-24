# Объявляем переменные ДО их первого использования
ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10

# --- ЭТАП 1: СБОРКА ЗАВИСИМОСТЕЙ В "ЧИСТОМ" ОКРУЖЕНИИ ---
FROM python:${PYTHON_VERSION}-slim as builder

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию
WORKDIR /deps

# Копируем файлы зависимостей
COPY etl/pyproject.toml etl/poetry.lock* ./

# Явно говорим Poetry создавать .venv в текущей папке (/deps)
RUN poetry config virtualenvs.in-project true

# Устанавливаем зависимости. Теперь папка /deps/.venv будет создана
RUN poetry install --no-root --only main --sync


# --- ЭТАП 2: ФИНАЛЬНЫЙ ОБРАЗ AIRFLOW ---
# Теперь используем объявленные ранее переменные
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Устанавливаем переменную окружения для PYTHONPATH
ENV PYTHONPATH="/opt/airflow/etl_src:${PYTHONPATH}"

# Копируем папку .venv с готовыми зависимостями из этапа builder
# Это решает все проблемы с правами доступа
USER root
COPY --from=builder /deps/.venv/ /home/airflow/.local/
RUN chown -R airflow:root /home/airflow/.local
USER airflow

# Копируем исходный код ETL и DAG'и
COPY --chown=airflow:airflow etl/src /opt/airflow/etl_src
COPY --chown=airflow:airflow etl/dags /opt/airflow/dags