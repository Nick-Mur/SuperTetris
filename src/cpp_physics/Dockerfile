# Dockerfile для C++ физического движка
FROM gcc:latest

WORKDIR /app

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    cmake \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование исходного кода
COPY . .

# Создание директории для сборки
RUN mkdir -p build

# Сборка проекта
RUN cd build && cmake .. && make

# Экспорт библиотеки
VOLUME /app/build

CMD ["tail", "-f", "/dev/null"]
