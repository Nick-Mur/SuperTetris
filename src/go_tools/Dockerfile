# Dockerfile для Go инструментов разработки
FROM golang:1.22.1

WORKDIR /app

# Копирование исходного кода
COPY . .

# Сборка проекта
RUN go build -o dev_tools

# Запуск сервиса
CMD ["./dev_tools"]
