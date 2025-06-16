ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER airflow

# Копируем файлы зависимостей ETL в домашнюю директорию пользователя
WORKDIR /home/airflow/etl
COPY ../../etl/pyproject.toml ../../etl/poetry.lock* ./

# Устанавливаем Poetry и зависимости ETL от имени пользователя airflow
RUN pip install --user --no-cache-dir "poetry==1.8.2"
RUN /home/airflow/.local/bin/poetry install --no-root --without dev

# Добавляем установленные пакеты в PYTHONPATH
ENV PYTHONPATH="/home/airflow/.local/lib/python3.10/site-packages:${PYTHONPATH}"

# Копируем DAG'и и исходный код ETL в стандартные директории Airflow
COPY ../../etl/dags /opt/airflow/dags
COPY ../../etl/src /opt/airflow/etl_src