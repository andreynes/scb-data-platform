# Используем официальный образ Airflow как базовый
ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Устанавливаем переменные окружения Airflow и Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AIRFLOW_HOME=/opt/airflow

# Переключаемся на пользователя airflow (если еще не он)
USER airflow

# Устанавливаем Poetry для пользователя airflow
RUN python -m pip install --user poetry==1.8.0
ENV PATH="/home/airflow/.local/bin:${PATH}"

# Создаем директорию для ETL проекта и его зависимостей (более явное создание)
RUN mkdir -p /opt/airflow/etl_project/etl_src \
    && mkdir -p /opt/airflow/dags \
    && mkdir -p /opt/airflow/ontology_repo_local_clone

# Устанавливаем рабочую директорию для файлов зависимостей ETL
WORKDIR /opt/airflow/etl_project

# Диагностика: Проверяем, что директория создана
RUN echo "Listing /opt/airflow/etl_project before copying poetry files:" \
    && ls -la /opt/airflow/etl_project

# Копируем файлы Poetry
# Убедись, что эти пути ./etl/... корректны относительно контекста сборки
COPY --chown=airflow:airflow ./etl/pyproject.toml ./etl/poetry.lock* /opt/airflow/etl_project/

# Диагностика: Проверяем, что файлы скопированы
RUN echo "Listing /opt/airflow/etl_project after copying poetry files:" \
    && ls -la /opt/airflow/etl_project

# Конфигурируем Poetry для создания venv в проекте
RUN poetry config virtualenvs.in-project true

# Устанавливаем зависимости ETL через Poetry
RUN echo "Attempting poetry install..." \
    && poetry install --no-interaction --no-ansi --no-root --sync \
    && echo "Poetry install finished."

# Диагностика: Проверяем, что .venv создан и содержит site-packages
RUN echo "Listing .venv contents:" \
    && ls -la /opt/airflow/etl_project/.venv/lib/python${PYTHON_VERSION}/site-packages/ \
    || echo ".venv/lib/pythonX.Y/site-packages not found or empty"

# Копируем исходный код ETL
COPY --chown=airflow:airflow ./etl/src /opt/airflow/etl_project/etl_src

# Копируем DAG'и в стандартную папку Airflow
COPY --chown=airflow:airflow ./etl/dags /opt/airflow/dags

# Копируем папку онтологии
COPY --chown=airflow:airflow ./ontology /opt/airflow/ontology_repo_local_clone

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="/opt/airflow/etl_project/.venv/lib/python${PYTHON_VERSION}/site-packages:/opt/airflow/etl_project/etl_src:${PYTHONPATH}"

# Возвращаемся в AIRFLOW_HOME
WORKDIR /opt/airflow