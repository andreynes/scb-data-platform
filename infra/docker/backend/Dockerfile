# --- Этап 1: Builder ---
FROM python:3.10-slim as builder

WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY backend/pyproject.toml backend/poetry.lock* ./

# Говорим poetry создавать .venv в папке /opt/venv
RUN poetry config virtualenvs.path /opt/venv

# Устанавливаем зависимости
RUN poetry install --no-root --sync


# --- Этап 2: Финальный образ ---
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение с зависимостями из /opt/venv
COPY --from=builder /opt/venv /opt/venv

# Копируем ИСХОДНЫЙ код, чтобы образ мог работать автономно
COPY backend/app ./app

# Устанавливаем PATH, чтобы исполняемые файлы из venv были доступны
ENV PATH="/opt/venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]