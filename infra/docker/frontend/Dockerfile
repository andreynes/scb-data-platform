# --- Этап 1: Установка зависимостей (deps) ---
FROM node:18-alpine as deps

WORKDIR /app

# Копируем package.json и lock-файл
COPY frontend/package.json frontend/package-lock.json* frontend/yarn.lock* ./

# Устанавливаем зависимости
RUN npm ci

# --- Этап 2: Запуск в режиме разработки (development) ---
FROM node:18-alpine

WORKDIR /app

# Копируем установленные зависимости с предыдущего этапа
COPY --from=deps /app/node_modules ./node_modules

# Копируем весь исходный код фронтенда
COPY frontend ./

# Открываем порт, который использует Vite
EXPOSE 5173

# Команда по умолчанию для запуска dev-сервера
CMD ["npm", "run", "dev"]