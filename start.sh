#!/bin/bash

# Скрипт запуска для Tetris с элементами Tricky Towers
# Поддерживает запуск на Linux, macOS и Windows (через WSL или MSYS2/MinGW)

set -e

# Определение цветов для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Определение корневой директории проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
LOG_DIR="${PROJECT_ROOT}/logs"
DATA_DIR="${PROJECT_ROOT}/data"
MODELS_DIR="${PROJECT_ROOT}/models"

# Создание необходимых директорий
mkdir -p "${LOG_DIR}"
mkdir -p "${DATA_DIR}"
mkdir -p "${MODELS_DIR}"
mkdir -p "${DIST_DIR}"

# Установка правильных прав доступа
chmod -R 755 "${LOG_DIR}"
chmod -R 755 "${DATA_DIR}"
chmod -R 755 "${MODELS_DIR}"
chmod -R 755 "${DIST_DIR}"

# Проверка зависимостей
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Проверка Python
    if ! command -v python &> /dev/null; then
        echo -e "${RED}Python not found. Please install Python 3.8 or higher.${NC}"
        exit 1
    fi
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js not found. Please install Node.js 18 or higher.${NC}"
        exit 1
    fi
    
    # Проверка npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}npm not found. Please install npm.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All dependencies are installed.${NC}"
}

# Функция ожидания готовности сервиса
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}Waiting for ${service_name} to be ready...${NC}"
    
    while ! nc -z localhost $port && [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Attempt $attempt/$max_attempts: ${service_name} is not ready yet...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo -e "${RED}${service_name} failed to start after $max_attempts attempts.${NC}"
        cleanup
        exit 1
    fi
    
    echo -e "${GREEN}${service_name} is ready!${NC}"
}

# Определение платформы
detect_platform() {
    case "$(uname -s)" in
        Linux*)     PLATFORM=linux;;
        Darwin*)    PLATFORM=macos;;
        CYGWIN*)    PLATFORM=windows;;
        MINGW*)     PLATFORM=windows;;
        MSYS*)      PLATFORM=windows;;
        *)          PLATFORM=unknown;;
    esac
    
    echo -e "${BLUE}Detected platform: ${PLATFORM}${NC}"
}

# Запуск Python серверной части
start_python_server() {
    echo -e "${BLUE}Starting Python Game Server...${NC}"
    
    cd "${PROJECT_ROOT}/src/python_server"
    python src/main.py > "${LOG_DIR}/python_server.log" 2>&1 &
    local PID=$!
    
    # Проверка успешности запуска
    sleep 2
    if ! ps -p $PID > /dev/null; then
        echo -e "${RED}Failed to start Python Game Server. Check logs for details.${NC}"
        exit 1
    fi
    
    # Ожидание готовности сервера
    wait_for_service "Python Game Server" 8000
    
    echo -e "${GREEN}Python Game Server started.${NC}"
}

# Запуск Python аналитики
start_python_analytics() {
    echo -e "${BLUE}Starting Python Analytics...${NC}"
    
    cd "${PROJECT_ROOT}/src/python_analytics"
    python src/main.py > "${LOG_DIR}/python_analytics.log" 2>&1 &
    
    echo -e "${GREEN}Python Analytics started.${NC}"
}

# Запуск Python ИИ
start_python_ai() {
    echo -e "${BLUE}Starting Python AI...${NC}"
    
    cd "${PROJECT_ROOT}/src/python_ai"
    python src/main.py > "${LOG_DIR}/python_ai.log" 2>&1 &
    
    echo -e "${GREEN}Python AI started.${NC}"
}

# Запуск TypeScript клиента
start_typescript_client() {
    echo -e "${BLUE}Starting TypeScript Client...${NC}"
    
    cd "${PROJECT_ROOT}/src/typescript_client"
    npm start > "${LOG_DIR}/typescript_client.log" 2>&1 &
    
    echo -e "${GREEN}TypeScript Client started.${NC}"
}

# Запуск C++ физического движка
start_cpp_physics() {
    echo -e "${BLUE}Starting C++ Physics Engine...${NC}"
    
    cd "${PROJECT_ROOT}/src/cpp_physics/build"
    ./physics_engine > "${LOG_DIR}/cpp_physics.log" 2>&1 &
    
    echo -e "${GREEN}C++ Physics Engine started.${NC}"
}

# Запуск Python инструментов
start_python_tools() {
    echo -e "${BLUE}Starting Python Development Tools...${NC}"
    
    PYTHON_DIR="${PROJECT_ROOT}/src/python_tools"
    
    cd "${PYTHON_DIR}"
    python main.py &
    
    echo -e "${GREEN}Python Development Tools started.${NC}"
}

# Обработка сигналов завершения
cleanup() {
    echo -e "${YELLOW}Shutting down all components...${NC}"
    
    # Остановка всех процессов
    pkill -f "python3 src/main.py" || true
    pkill -f "npm start" || true
    pkill -f "./physics_engine" || true
    pkill -f "./dev_tools" || true
    
    echo -e "${GREEN}All components stopped.${NC}"
    exit 0
}

# Регистрация обработчика сигналов
trap cleanup SIGINT SIGTERM

# Основная функция
main() {
    echo -e "${BLUE}Starting Tetris with Tricky Towers elements...${NC}"
    
    # Проверка зависимостей
    check_dependencies
    
    # Определение платформы
    detect_platform
    
    # Запуск компонентов в правильном порядке
    start_cpp_physics
    wait_for_service "C++ Physics Engine" 9000
    
    start_python_server
    wait_for_service "Python Game Server" 8000
    
    start_python_analytics
    wait_for_service "Python Analytics" 8001
    
    start_python_ai
    wait_for_service "Python AI" 8002
    
    start_typescript_client
    wait_for_service "TypeScript Client" 3000
    
    start_python_tools
    wait_for_service "Python Development Tools" 8080
    
    echo -e "${GREEN}All components started successfully!${NC}"
    echo -e "Open http://localhost:3000 in your browser to play the game."
    
    # Ожидание сигнала завершения
    wait
}

# Запуск основной функции
main 