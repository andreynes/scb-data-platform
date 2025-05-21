# Этап 1: Базовый образ с Python и Poetry
FROM python:3.10-slim as base

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION 1
ENV POETRY_VIRTUALENVS_CREATE false
# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем только файлы зависимостей для кэширования этого слоя
COPY ./backend/pyproject.toml ./backend/poetry.lock* /app/backend/

# Устанавливаем зависимости проекта, не включая сам проект (no-root)
# и не включая dev-зависимости для production-like окружения
# Для разработки можно было бы убрать --no-dev, но для MVP оставим так
RUN cd /app/backend && poetry install --no-root --no-dev --sync

# Этап 2: Финальный образ
FROM base as development

# Копируем остальной код приложения
# Предполагается, что для разработки мы будем монтировать volume,
# но этот COPY важен для сборки образа, если volume не используется.
COPY ./backend/app /app/backend/app

# Устанавливаем рабочую директорию для запуска
WORKDIR /app/backend

# Порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения с Uvicorn и hot-reloading
# Для production --reload нужно убрать
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]