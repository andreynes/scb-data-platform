# Финальная, правильная версия Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Копируем файл с зависимостями из папки backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ код из папки backend в текущую директорию (/app)
COPY backend/ .

# Команда запуска ищет main.py в текущей директории (/app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]