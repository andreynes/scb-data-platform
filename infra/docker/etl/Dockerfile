ARG AIRFLOW_VERSION=2.8.1
ARG PYTHON_VERSION=3.10
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER airflow
COPY etl/requirements.txt /tmp/requirements.txt
RUN pip install --user -r /tmp/requirements.txt
COPY --chown=airflow:airflow etl/dags ./dags
COPY --chown=airflow:airflow etl/src ./etl_src