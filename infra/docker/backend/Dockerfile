FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION 1
ENV POETRY_VIRTUALENVS_CREATE false
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VERSION="2.1.3" 
ENV PATH="$POETRY_HOME/bin:$PATH"

# Установка Poetry - ваш метод рабочий, но можно и через pip, как в примере из плана
# Оставим ваш метод, он более явный для версии
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} && \
    poetry --version

# Устанавливаем рабочую директорию, куда будут копироваться файлы проекта бэкенда
WORKDIR /app/backend 

# Копируем pyproject.toml и poetry.lock в /app/backend/
COPY backend/pyproject.toml backend/poetry.lock* ./ 
# ./ здесь означает текущий WORKDIR, т.е. /app/backend/

# Устанавливаем зависимости (Poetry найдет pyproject.toml в текущей директории)
RUN poetry install --no-root --sync -vvv 
# --no-dev убрано, так как для разработки с --reload зависимости разработки могут быть нужны. 
# Если образ только для production, то --no-dev нужно оставить.

# Копируем код приложения бэкенда в /app/backend/app/
COPY backend/app ./app 

EXPOSE 8000

# WORKDIR /app # <--- ЭТА СТРОКА БЫЛА ПРОБЛЕМОЙ, УДАЛЯЕМ ЕЕ ИЛИ ОСТАВЛЯЕМ ПРЕДЫДУЩИЙ WORKDIR

# Команда запуска Uvicorn. WORKDIR уже /app/backend, поэтому Poetry найдет pyproject.toml
# и uvicorn найдет backend.app.main:app как app.main:app (относительно /app/backend)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Обратите внимание: команда для --reload в docker-compose.yml переопределит этот CMD.
# Этот CMD будет использоваться, если вы запустите образ напрямую через docker run без переопределения команды.