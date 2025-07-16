# Используем официальный образ Airflow как базовый
FROM apache/airflow:2.8.1-python3.10

# КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ: Устанавливаем проблемный пакет отдельно и в первую очередь
# Используем --user, чтобы установить его в домашнюю директорию пользователя airflow, избегая проблем с правами
RUN pip install --no-cache-dir --user Flask-Session==0.5.0

# Копируем файл с остальными зависимостями
COPY etl/requirements.txt /requirements.txt

# Устанавливаем остальные зависимости
RUN pip install --no-cache-dir --user -r /requirements.txt

# Копируем наш код
COPY etl/dags /opt/airflow/dags
COPY etl/src /opt/airflow/etl_src

# Добавляем путь к --user пакетам и нашему коду в PYTHONPATH
# Это гарантирует, что Python будет искать модули в правильном месте
ENV PYTHONPATH="/home/airflow/.local/lib/python3.10/site-packages:/opt/airflow/etl_src:${PYTHONPATH}"