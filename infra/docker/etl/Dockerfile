# Кастомный образ Airflow
ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER root
# (Опционально) Установка системных зависимостей, если они понадобятся
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq-dev \
#     ghostscript \
#   && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

WORKDIR /opt/airflow

# Устанавливаем зависимости Python из файла requirements.txt
# Путь указан от корня проекта, так как контекст сборки - корень
COPY etl/requirements.txt /tmp/requirements.txt
RUN pip install --user -r /tmp/requirements.txt

# Копируем DAG'и и исходный код ETL
# Пути также указаны от корня проекта
COPY --chown=airflow:airflow etl/dags ./dags
COPY --chown=airflow:airflow etl/src ./etl_src

# (Опционально) Если есть плагины
# COPY --chown=airflow:airflow etl/plugins ./plugins