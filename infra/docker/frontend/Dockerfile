# Этап 1: Установка зависимостей
FROM node:18-alpine AS deps
# Используем Alpine для меньшего размера образа

WORKDIR /app

# Копируем package.json и lock-файл
COPY ./frontend/package.json ./frontend/package-lock.json* ./frontend/yarn.lock* ./
# Если используете yarn, замените package-lock.json* на yarn.lock

# Устанавливаем зависимости
# Если используете yarn, замените `npm ci` на `yarn install --frozen-lockfile`
RUN npm ci

# Этап 2: Образ для разработки
FROM node:18-alpine AS development

WORKDIR /app

# Копируем зависимости из предыдущего этапа
COPY --from=deps /app/node_modules ./node_modules

# Копируем остальной код фронтенда
COPY ./frontend /app

# EXPOSE 5173 # Vite сам сообщит порт, на котором запустится
# CMD ["npm", "run", "dev", "--", "--host"] # --host нужен, чтобы Vite был доступен извне контейнера
CMD ["npm", "run", "dev", "--", "--host"]