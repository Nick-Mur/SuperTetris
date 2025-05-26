# Dockerfile для Rust серверной части
FROM rust:latest

WORKDIR /app

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем все файлы проекта
COPY . .

# Собираем проект
RUN cargo build --release

# Открытие портов
EXPOSE 8080
EXPOSE 8081

# Запуск сервера
CMD ["./target/release/tetris_server", "--config", "/app/config/config.json"]
