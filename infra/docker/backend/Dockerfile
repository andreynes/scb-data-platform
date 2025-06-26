# infra/docker/backend/Dockerfile

# --- Этап 1: Сборщик зависимостей ---
FROM python:3.10-slim as builder

RUN pip install poetry
WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock* ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --without dev --sync --no-root


# --- Этап 2: Финальный образ ---
FROM python:3.10-slim

WORKDIR /app

# Копируем .venv и код
COPY --from=builder /app/.venv ./.venv
COPY backend/ ./

# Устанавливаем PATH, чтобы uvicorn был доступен
ENV PATH="/app/.venv/bin:$PATH"

# Команда по умолчанию
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]