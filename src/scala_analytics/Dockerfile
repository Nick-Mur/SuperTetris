# Dockerfile для Scala аналитики
FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Установка SBT
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L -o sbt.deb https://repo.scala-sbt.org/scalasbt/debian/sbt-1.9.6.deb && \
    dpkg -i sbt.deb && \
    rm sbt.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование исходного кода
COPY . .

# Сборка проекта
RUN sbt clean assembly

# Запуск сервиса
CMD ["java", "-jar", "target/scala-2.13/tetris-towers-analytics-assembly-1.0.0.jar"]
