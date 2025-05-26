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

# Запуск C++ физического движка
start_cpp_physics() {
    echo -e "${BLUE}Starting C++ Physics Engine...${NC}"
    
    if [ "$PLATFORM" = "windows" ]; then
        "${DIST_DIR}/bin/physics_engine.exe" > "${LOG_DIR}/physics_engine.log" 2>&1 &
    else
        "${DIST_DIR}/bin/physics_engine" > "${LOG_DIR}/physics_engine.log" 2>&1 &
    fi
    
    echo -e "${GREEN}C++ Physics Engine started.${NC}"
}

# Запуск Rust серверной части
start_rust_server() {
    echo -e "${BLUE}Starting Rust Game Server...${NC}"
    
    if [ "$PLATFORM" = "windows" ]; then
        "${DIST_DIR}/bin/tetris_server.exe" --config "${PROJECT_ROOT}/config/server.toml" > "${LOG_DIR}/rust_server.log" 2>&1 &
    else
        "${DIST_DIR}/bin/tetris_server" --config "${PROJECT_ROOT}/config/server.toml" > "${LOG_DIR}/rust_server.log" 2>&1 &
    fi
    
    echo -e "${GREEN}Rust Game Server started.${NC}"
}

# Запуск Python игровой логики
start_python_logic() {
    echo -e "${BLUE}Starting Python Game Logic...${NC}"
    
    cd "${DIST_DIR}/python"
    python3 main.py > "${LOG_DIR}/python_logic.log" 2>&1 &
    
    echo -e "${GREEN}Python Game Logic started.${NC}"
}

# Запуск TypeScript клиентской части
start_typescript_client() {
    echo -e "${BLUE}Starting TypeScript Client...${NC}"
    
    cd "${DIST_DIR}/client"
    npm start > "${LOG_DIR}/typescript_client.log" 2>&1 &
    
    echo -e "${GREEN}TypeScript Client started.${NC}"
}

# Запуск Julia ИИ системы
start_julia_ai() {
    echo -e "${BLUE}Starting Julia AI System...${NC}"
    
    cd "${DIST_DIR}/julia"
    julia main.jl > "${LOG_DIR}/julia_ai.log" 2>&1 &
    
    echo -e "${GREEN}Julia AI System started.${NC}"
}

# Запуск Go инструментов разработки
start_go_tools() {
    echo -e "${BLUE}Starting Go Development Tools...${NC}"
    
    if [ "$PLATFORM" = "windows" ]; then
        "${DIST_DIR}/bin/dev_tools.exe" > "${LOG_DIR}/go_tools.log" 2>&1 &
    else
        "${DIST_DIR}/bin/dev_tools" > "${LOG_DIR}/go_tools.log" 2>&1 &
    fi
    
    echo -e "${GREEN}Go Development Tools started.${NC}"
}

# Запуск Scala аналитики
start_scala_analytics() {
    echo -e "${BLUE}Starting Scala Analytics...${NC}"
    
    cd "${DIST_DIR}/scala"
    sbt run > "${LOG_DIR}/scala_analytics.log" 2>&1 &
    
    echo -e "${GREEN}Scala Analytics started.${NC}"
}

# Обработка сигналов завершения
cleanup() {
    echo -e "${YELLOW}Shutting down all components...${NC}"
    
    # Остановка всех процессов
    pkill -f "physics_engine" || true
    pkill -f "tetris_server" || true
    pkill -f "python3 main.py" || true
    pkill -f "npm start" || true
    pkill -f "julia main.jl" || true
    pkill -f "dev_tools" || true
    pkill -f "sbt run" || true
    
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
    start_cpp_physics
    start_rust_server
    start_python_logic
    start_typescript_client
    start_julia_ai
    start_go_tools
    start_scala_analytics
    
    echo -e "${GREEN}All components started successfully.${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop all components.${NC}"
    
    # Ожидание завершения
    wait
}

# Запуск основной функции
main 