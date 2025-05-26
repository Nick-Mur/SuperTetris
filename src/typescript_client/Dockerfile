# Dockerfile для TypeScript клиентской части
FROM node:20.11.1-alpine

WORKDIR /app

# Установка зависимостей
COPY package.json package-lock.json* ./
RUN npm install

# Копирование исходного кода
COPY . .

# Сборка проекта
RUN npm run build

# Открытие порта
EXPOSE 3000

# Запуск клиента
CMD ["npm", "start"]
