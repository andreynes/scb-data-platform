# Этап 1: Сборка зависимостей
FROM python:3.10-slim as builder

WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# ВАЖНО: Настраиваем Poetry, чтобы он создавал .venv внутри папки проекта
RUN poetry config virtualenvs.in-project true

# Копируем файлы проекта. Важно скопировать их до `poetry install`
COPY ./backend/pyproject.toml ./backend/poetry.lock* ./

# Теперь poetry install создаст .venv прямо в /app/
# И мы используем --without dev, как и обсуждали
RUN poetry install --without dev --no-root -E async --sync


# Этап 2: Финальный образ
FROM python:3.10-slim

WORKDIR /app

# Эта команда теперь будет работать, т.к. .venv находится в /app/
COPY --from=builder /app/.venv /app/.venv

# Копируем исходный код приложения
COPY ./backend/app /app/app

# Команда для запуска приложения через Python из нашего .venv
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]