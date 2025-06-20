# Этап 1: Сборка зависимостей с помощью Poetry
FROM python:3.10-slim as builder

WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы управления зависимостями в корень рабочей директории
COPY backend/pyproject.toml backend/poetry.lock* ./

# Говорим poetry создавать .venv внутри этой папки
RUN poetry config virtualenvs.in-project true

# Устанавливаем зависимости
RUN poetry install --no-root --sync


# Этап 2: Финальный, легковесный образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем PATH, чтобы исполняемые файлы из .venv были доступны напрямую
ENV PATH="/app/.venv/bin:$PATH"

# Копируем виртуальное окружение с зависимостями с предыдущего этапа
COPY --from=builder /app/.venv ./.venv

# Копируем исходный код нашего приложения в подпапку 'app'
COPY backend/app ./app

# Команда для запуска приложения по умолчанию.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]