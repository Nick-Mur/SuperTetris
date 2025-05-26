#!/bin/bash
# Запуск всех компонентов игры

# Запуск физического движка
./bin/physics_engine &
PHYSICS_PID=$!

# Запуск серверной части
./bin/game_server &
SERVER_PID=$!

# Запуск системы ИИ
./bin/ai_system &
AI_PID=$!

# Запуск системы аналитики
java -jar lib/analytics-assembly-1.0.jar &
ANALYTICS_PID=$!

# Открытие игры в браузере
sleep 2
xdg-open http://localhost:3000

# Функция для корректного завершения всех процессов
function cleanup {
  echo "Завершение работы..."
  kill $PHYSICS_PID $SERVER_PID $AI_PID $ANALYTICS_PID
  exit 0
}

# Перехват сигнала завершения
trap cleanup SIGINT SIGTERM

# Ожидание завершения
echo "Игра запущена. Нажмите Ctrl+C для завершения."
wait
