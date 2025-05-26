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

# Создание необходимых директорий
mkdir -p "${LOG_DIR}"

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

# Запуск Go инструментов
start_go_tools() {
    echo -e "${BLUE}Starting Go Development Tools...${NC}"
    
    cd "${PROJECT_ROOT}/src/go_tools"
    ./dev_tools > "${LOG_DIR}/go_tools.log" 2>&1 &
    
    echo -e "${GREEN}Go Development Tools started.${NC}"
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
    
    # Определение платформы
    detect_platform
    
    # Запуск компонентов
    start_python_server
    start_python_analytics
    start_python_ai
    start_typescript_client
    start_cpp_physics
    start_go_tools
    
    echo -e "${GREEN}All components started successfully!${NC}"
    echo -e "Open http://localhost:3000 in your browser to play the game."
}

# Запуск основной функции
main 