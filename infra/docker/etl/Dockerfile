ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER airflow

# Копируем файл с зависимостями
COPY etl/requirements.txt /requirements.txt

# Устанавливаем зависимости через pip
RUN pip install --user --no-cache-dir -r /requirements.txt

# Копируем исходный код ETL. Airflow сам добавит /opt/airflow/dags в путь.
# Нам нужно добавить только папку с исходниками.
COPY --chown=airflow:airflow etl/src /opt/airflow/etl_src

# Добавляем нашу папку с исходниками в PYTHONPATH
ENV PYTHONPATH="/opt/airflow/etl_src:${PYTHONPATH}"

USER airflow