FROM apache/airflow:2.8.1-python3.10

# Устанавливаем только самые необходимые системные зависимости
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER airflow

# Копируем и устанавливаем все зависимости одной командой
COPY --chown=airflow:airflow etl/requirements.txt /tmp/requirements.txt
RUN pip install --user --no-cache-dir -r /tmp/requirements.txt

# Копируем весь код ETL
COPY --chown=airflow:airflow etl /opt/airflow/etl