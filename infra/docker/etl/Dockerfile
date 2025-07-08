# infra/docker/etl/Dockerfile (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ)

# Используем официальный образ Airflow как базу
FROM apache/airflow:2.8.1-python3.10

# Устанавливаем переменные окружения
ENV AIRFLOW_HOME=/opt/airflow
# Добавляем корень Airflow в пути поиска Python, чтобы работали импорты из папки 'etl'
ENV PYTHONPATH="${AIRFLOW_HOME}:${PYTHONPATH}"

# Переключаемся на пользователя airflow для безопасности
USER airflow

# --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ---
# Принудительно устанавливаем версию Pydantic, совместимую с Airflow 2.8,
# чтобы избежать конфликтов с зависимостями из нашего requirements.txt.
# Это нужно сделать ДО установки остальных пакетов.
RUN pip install --user "pydantic<2"

# --- УСТАНОВКА ЗАВИСИМОСТЕЙ ПРОЕКТА ---
# Копируем файл с нашими зависимостями
COPY --chown=airflow:airflow etl/requirements.txt /tmp/requirements.txt

# Устанавливаем зависимости из requirements.txt
# --user устанавливает пакеты в домашнюю директорию пользователя airflow
RUN pip install --user --no-cache-dir --timeout=100 -r /tmp/requirements.txt

# --- КОПИРОВАНИЕ КОДА ПРОЕКТА ---
# Копируем папку с DAG'ами в стандартную директорию
COPY --chown=airflow:airflow etl/dags ./dags

# Копируем всю папку 'etl' (включая папку 'src' внутри нее) в корень /opt/airflow
# Это позволит импортам вида 'from etl.src...' работать корректно
COPY --chown=airflow:airflow etl ./etl

# Команда по умолчанию будет переопределена в docker-compose.yml для каждого сервиса
CMD ["airflow", "standalone"]