#!/bin/bash

# Скрипт системного тестирования для Tetris с элементами Tricky Towers
# Поддерживает тестирование на Linux, macOS и Windows (через WSL или MSYS2/MinGW)

set -e

# Определение цветов для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Определение корневой директории проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${PROJECT_ROOT}/tests"
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

# Тестирование C++ физического движка
test_cpp_physics() {
    echo -e "${BLUE}Testing C++ Physics Engine...${NC}"
    
    cd "${PROJECT_ROOT}/src/cpp_physics"
    
    if [ "$PLATFORM" = "windows" ]; then
        ./build/test/physics_engine_test.exe > "${LOG_DIR}/physics_engine_test.log" 2>&1
    else
        ./build/test/physics_engine_test > "${LOG_DIR}/physics_engine_test.log" 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}C++ Physics Engine tests passed.${NC}"
    else
        echo -e "${RED}C++ Physics Engine tests failed.${NC}"
        exit 1
    fi
}

# Тестирование Rust серверной части
test_rust_server() {
    echo -e "${BLUE}Testing Rust Game Server...${NC}"
    
    cd "${PROJECT_ROOT}/src/rust_server"
    cargo test > "${LOG_DIR}/rust_server_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Rust Game Server tests passed.${NC}"
    else
        echo -e "${RED}Rust Game Server tests failed.${NC}"
        exit 1
    fi
}

# Тестирование Python игровой логики
test_python_logic() {
    echo -e "${BLUE}Testing Python Game Logic...${NC}"
    
    cd "${PROJECT_ROOT}/src/python_logic"
    python3 -m pytest > "${LOG_DIR}/python_logic_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Python Game Logic tests passed.${NC}"
    else
        echo -e "${RED}Python Game Logic tests failed.${NC}"
        exit 1
    fi
}

# Тестирование TypeScript клиентской части
test_typescript_client() {
    echo -e "${BLUE}Testing TypeScript Client...${NC}"
    
    cd "${PROJECT_ROOT}/src/typescript_client"
    npm test > "${LOG_DIR}/typescript_client_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}TypeScript Client tests passed.${NC}"
    else
        echo -e "${RED}TypeScript Client tests failed.${NC}"
        exit 1
    fi
}

# Тестирование Julia ИИ системы
test_julia_ai() {
    echo -e "${BLUE}Testing Julia AI System...${NC}"
    
    cd "${PROJECT_ROOT}/src/julia_ai"
    julia -e 'using Pkg; Pkg.test()' > "${LOG_DIR}/julia_ai_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Julia AI System tests passed.${NC}"
    else
        echo -e "${RED}Julia AI System tests failed.${NC}"
        exit 1
    fi
}

# Тестирование Go инструментов разработки
test_go_tools() {
    echo -e "${BLUE}Testing Go Development Tools...${NC}"
    
    cd "${PROJECT_ROOT}/src/go_tools"
    go test ./... > "${LOG_DIR}/go_tools_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Go Development Tools tests passed.${NC}"
    else
        echo -e "${RED}Go Development Tools tests failed.${NC}"
        exit 1
    fi
}

# Тестирование Scala аналитики
test_scala_analytics() {
    echo -e "${BLUE}Testing Scala Analytics...${NC}"
    
    cd "${PROJECT_ROOT}/src/scala_analytics"
    sbt test > "${LOG_DIR}/scala_analytics_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Scala Analytics tests passed.${NC}"
    else
        echo -e "${RED}Scala Analytics tests failed.${NC}"
        exit 1
    fi
}

# Интеграционное тестирование
test_integration() {
    echo -e "${BLUE}Running integration tests...${NC}"
    
    cd "${TEST_DIR}"
    python3 run_integration_tests.py > "${LOG_DIR}/integration_test.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Integration tests passed.${NC}"
    else
        echo -e "${RED}Integration tests failed.${NC}"
        exit 1
    fi
}

# Основная функция
main() {
    echo -e "${BLUE}Starting system tests...${NC}"
    
    # Определение платформы
    detect_platform
    
    # Запуск тестов
    test_cpp_physics
    test_rust_server
    test_python_logic
    test_typescript_client
    test_julia_ai
    test_go_tools
    test_scala_analytics
    test_integration
    
    echo -e "${GREEN}All tests passed successfully.${NC}"
}

# Запуск основной функции
main
