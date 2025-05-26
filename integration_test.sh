#!/bin/bash

# Скрипт интеграционного тестирования для Tetris с элементами Tricky Towers

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Пути
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"

# Создание директории для логов
mkdir -p "${LOG_DIR}"

# Проверка Python компонентов
if [ ! -f "src/python_server/src/main.py" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код серверной части (Python)${NC}"
    exit 1
fi

if [ ! -f "src/python_analytics/src/main.py" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код системы аналитики (Python)${NC}"
    exit 1
fi

if [ ! -f "src/python_ai/src/main.py" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код ИИ (Python)${NC}"
    exit 1
fi

# Проверка TypeScript компонентов
if [ ! -f "src/typescript_client/src/App.tsx" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код клиентской части (TypeScript)${NC}"
    exit 1
fi

# Проверка C++ компонентов
if [ ! -f "src/cpp_physics/src/physics_engine.cpp" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код физического движка (C++)${NC}"
    exit 1
fi

# Проверка Go компонентов
if [ ! -f "src/go_tools/dev_tools.go" ]; then
    echo -e "${RED}ОШИБКА: Отсутствует исходный код инструментов разработки (Go)${NC}"
    exit 1
fi

# Запуск интеграционных тестов
echo -e "${BLUE}Запуск интеграционных тестов...${NC}"

# Тестирование Python серверной части
echo "Testing Python Game Server..."
cd "${PROJECT_ROOT}/src/python_server"
python -m pytest tests/integration/ > "${LOG_DIR}/python_server_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Python Game Server integration tests passed.${NC}"
else
    echo -e "${RED}Python Game Server integration tests failed.${NC}"
    exit 1
fi

# Тестирование Python аналитики
echo "Testing Python Analytics..."
cd "${PROJECT_ROOT}/src/python_analytics"
python -m pytest tests/integration/ > "${LOG_DIR}/python_analytics_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Python Analytics integration tests passed.${NC}"
else
    echo -e "${RED}Python Analytics integration tests failed.${NC}"
    exit 1
fi

# Тестирование Python ИИ
echo "Testing Python AI..."
cd "${PROJECT_ROOT}/src/python_ai"
python -m pytest tests/integration/ > "${LOG_DIR}/python_ai_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Python AI integration tests passed.${NC}"
else
    echo -e "${RED}Python AI integration tests failed.${NC}"
    exit 1
fi

# Тестирование TypeScript клиента
echo "Testing TypeScript Client..."
cd "${PROJECT_ROOT}/src/typescript_client"
npm run test:integration > "${LOG_DIR}/typescript_client_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}TypeScript Client integration tests passed.${NC}"
else
    echo -e "${RED}TypeScript Client integration tests failed.${NC}"
    exit 1
fi

# Тестирование C++ физического движка
echo "Testing C++ Physics Engine..."
cd "${PROJECT_ROOT}/src/cpp_physics/build"
ctest --output-on-failure > "${LOG_DIR}/cpp_physics_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}C++ Physics Engine integration tests passed.${NC}"
else
    echo -e "${RED}C++ Physics Engine integration tests failed.${NC}"
    exit 1
fi

# Тестирование Go инструментов
echo "Testing Go Development Tools..."
cd "${PROJECT_ROOT}/src/go_tools"
go test -v ./... > "${LOG_DIR}/go_tools_integration.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Go Development Tools integration tests passed.${NC}"
else
    echo -e "${RED}Go Development Tools integration tests failed.${NC}"
    exit 1
fi

echo -e "${GREEN}All integration tests passed successfully!${NC}"
