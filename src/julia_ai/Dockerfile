# Dockerfile для Julia ИИ
FROM julia:1.9.4

WORKDIR /app

# Копирование исходного кода
COPY . .

# Установка зависимостей
RUN julia -e 'using Pkg; Pkg.activate("."); Pkg.instantiate()'

# Запуск сервиса
CMD ["julia", "ai_system.jl"]
