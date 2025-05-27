#!/bin/bash

# Универсальный скрипт сборки для Tetris с элементами Tricky Towers
# Поддерживает сборку на Linux, macOS и Windows (через WSL или MSYS2/MinGW)

set -e

# Определение цветов для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Определение корневой директории проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
DIST_DIR="${PROJECT_ROOT}/dist"
LOG_DIR="${PROJECT_ROOT}/logs"

# Создание необходимых директорий
mkdir -p "${BUILD_DIR}" "${DIST_DIR}" "${LOG_DIR}"

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

# Проверка наличия необходимых инструментов
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Список необходимых инструментов
    DEPS=("cmake" "python3" "npm" "go")
    MISSING=()
    
    for dep in "${DEPS[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            MISSING+=("$dep")
        fi
    done
    
    if [ ${#MISSING[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies: ${MISSING[*]}${NC}"
        echo -e "${YELLOW}Please install the missing dependencies and try again.${NC}"
        
        case "$PLATFORM" in
            linux)
                echo -e "${YELLOW}You can install them using your package manager:${NC}"
                echo "sudo apt-get install build-essential cmake python3-dev python3-pip nodejs npm golang"
                ;;
            macos)
                echo -e "${YELLOW}You can install them using Homebrew:${NC}"
                echo "brew install cmake python node go"
                ;;
            windows)
                echo -e "${YELLOW}You can install them using Chocolatey:${NC}"
                echo "choco install cmake python nodejs golang"
                ;;
        esac
        
        exit 1
    fi
    
    echo -e "${GREEN}All dependencies are installed.${NC}"
}

# Сборка Python серверной части
build_python_server() {
    echo -e "${BLUE}Building Python Game Server...${NC}"
    
    PYTHON_DIR="${PROJECT_ROOT}/src/python_server"
    
    cd "${PYTHON_DIR}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python Game Server built successfully.${NC}"
}

# Сборка Python аналитики
build_python_analytics() {
    echo -e "${BLUE}Building Python Analytics System...${NC}"
    
    ANALYTICS_DIR="${PROJECT_ROOT}/src/python_analytics"
    
    cd "${ANALYTICS_DIR}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python Analytics System built successfully.${NC}"
}

# Сборка Python ИИ
build_python_ai() {
    echo -e "${BLUE}Building Python AI System...${NC}"
    
    AI_DIR="${PROJECT_ROOT}/src/python_ai"
    
    cd "${AI_DIR}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python AI System built successfully.${NC}"
}

# Сборка TypeScript клиента
build_typescript_client() {
    echo -e "${BLUE}Building TypeScript Client...${NC}"
    
    CLIENT_DIR="${PROJECT_ROOT}/src/typescript_client"
    
    cd "${CLIENT_DIR}"
    npm install
    npm run build
    
    echo -e "${GREEN}TypeScript Client built successfully.${NC}"
}

# Сборка C++ физического движка
build_cpp_physics() {
    echo -e "${BLUE}Building C++ Physics Engine...${NC}"
    
    PHYSICS_DIR="${PROJECT_ROOT}/src/cpp_physics"
    
    cd "${PHYSICS_DIR}"
    mkdir -p build
    cd build
    cmake ..
    make
    
    echo -e "${GREEN}C++ Physics Engine built successfully.${NC}"
}

# Сборка Python инструментов
build_python_tools() {
    echo -e "${BLUE}Building Python Development Tools...${NC}"
    
    PYTHON_DIR="${PROJECT_ROOT}/src/python_tools"
    DIST_DIR="${PROJECT_ROOT}/dist"
    
    cd "${PYTHON_DIR}"
    python -m pip install -r requirements.txt
    python -m PyInstaller --onefile main.py -o "${DIST_DIR}/bin/dev_tools"
    
    echo -e "${GREEN}Python Development Tools built successfully.${NC}"
}

# Создание конфигурационных файлов
create_config_files() {
    echo -e "${BLUE}Creating configuration files...${NC}"
    
    CONFIG_DIR="${DIST_DIR}/config"
    mkdir -p "${CONFIG_DIR}"
    
    # Создание основного конфигурационного файла
    cat > "${CONFIG_DIR}/config.json" << EOF
{
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "ws_port": 8081
    },
    "database": {
        "type": "sqlite",
        "path": "../data/tetris.db"
    },
    "physics": {
        "gravity": 9.8,
        "friction": 0.1,
        "restitution": 0.5
    },
    "game": {
        "max_players": 4,
        "tick_rate": 60,
        "block_types": ["I", "J", "L", "O", "S", "T", "Z"],
        "spell_types": ["FREEZE", "WEIGHT", "GHOST", "BOMB", "SHIELD"]
    },
    "ai": {
        "difficulty_levels": ["EASY", "MEDIUM", "HARD", "EXPERT"],
        "model_path": "../data/ai_models"
    },
    "analytics": {
        "enabled": true,
        "log_level": "INFO",
        "data_path": "../data/analytics"
    },
    "paths": {
        "logs": "../logs",
        "data": "../data",
        "assets": "../assets"
    }
}
EOF
    
    # Создание конфигурационного файла для логирования
    cat > "${CONFIG_DIR}/logging.json" << EOF
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "../logs/tetris.log",
            "maxBytes": 10485760,
            "backupCount": 5
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": true
        }
    }
}
EOF
    
    echo -e "${GREEN}Configuration files created successfully.${NC}"
}

# Создание скриптов запуска
create_launch_scripts() {
    echo -e "${BLUE}Creating launch scripts...${NC}"
    
    # Создание скрипта запуска для Linux/macOS
    cat > "${DIST_DIR}/start.sh" << EOF
#!/bin/bash

# Скрипт запуска Tetris с элементами Tricky Towers

# Определение корневой директории
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
cd "\${SCRIPT_DIR}"

# Создание необходимых директорий
mkdir -p logs data

# Запуск сервера в фоновом режиме
echo "Starting Tetris Towers server..."
./bin/tetris_server --config ./config/config.json > ./logs/server.log 2>&1 &
SERVER_PID=\$!

# Ожидание запуска сервера
echo "Waiting for server to start..."
sleep 2

# Запуск клиента
echo "Starting Tetris Towers client..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8080
elif command -v open &> /dev/null; then
    open http://localhost:8080
else
    echo "Please open http://localhost:8080 in your browser."
fi

# Обработка сигнала завершения
trap "echo 'Stopping Tetris Towers...'; kill \$SERVER_PID; exit 0" SIGINT SIGTERM

# Ожидание завершения сервера
wait \$SERVER_PID
EOF
    
    # Создание скрипта запуска для Windows
    cat > "${DIST_DIR}/start.bat" << EOF
@echo off
REM Скрипт запуска Tetris с элементами Tricky Towers

REM Переход в директорию скрипта
cd /d "%~dp0"

REM Создание необходимых директорий
if not exist logs mkdir logs
if not exist data mkdir data

REM Запуск сервера в фоновом режиме
echo Starting Tetris Towers server...
start /b bin\tetris_server.exe --config config\config.json > logs\server.log 2>&1

REM Ожидание запуска сервера
echo Waiting for server to start...
timeout /t 2 > nul

REM Запуск клиента
echo Starting Tetris Towers client...
start http://localhost:8080

echo Press Ctrl+C to stop the server.
pause
EOF
    
    # Установка прав на выполнение для скрипта запуска на Linux/macOS
    if [ "$PLATFORM" != "windows" ]; then
        chmod +x "${DIST_DIR}/start.sh"
    fi
    
    echo -e "${GREEN}Launch scripts created successfully.${NC}"
}

# Создание документации
create_documentation() {
    echo -e "${BLUE}Creating documentation...${NC}"
    
    DOC_DIR="${DIST_DIR}/docs"
    mkdir -p "${DOC_DIR}"
    
    # Копирование README и других документов
    cp "${PROJECT_ROOT}/README.md" "${DOC_DIR}/"
    cp -r "${PROJECT_ROOT}/docs"/* "${DOC_DIR}/" 2>/dev/null || true
    cp "${PROJECT_ROOT}/src/integration/README.md" "${DOC_DIR}/integration.md"
    
    echo -e "${GREEN}Documentation created successfully.${NC}"
}

# Создание архива с собранным проектом
create_archive() {
    echo -e "${BLUE}Creating distribution archive...${NC}"
    
    cd "${PROJECT_ROOT}"
    
    ARCHIVE_NAME="tetris_towers_${PLATFORM}.zip"
    
    if [ "$PLATFORM" = "windows" ]; then
        powershell -Command "Compress-Archive -Path ${DIST_DIR}/* -DestinationPath ${PROJECT_ROOT}/${ARCHIVE_NAME}"
    else
        (cd "${DIST_DIR}" && zip -r "${PROJECT_ROOT}/${ARCHIVE_NAME}" .)
    fi
    
    echo -e "${GREEN}Distribution archive created: ${ARCHIVE_NAME}${NC}"
}

# Запуск тестов
run_tests() {
    echo -e "${BLUE}Running tests...${NC}"
    
    # Запуск тестов Python серверной части
    echo "Running Python Game Server tests..."
    cd "${PROJECT_ROOT}/src/python_server"
    python -m pytest tests/
    
    # Запуск тестов Python аналитики
    echo "Running Python Analytics tests..."
    cd "${PROJECT_ROOT}/src/python_analytics"
    python -m pytest tests/
    
    # Запуск тестов Python ИИ
    echo "Running Python AI tests..."
    cd "${PROJECT_ROOT}/src/python_ai"
    python -m pytest tests/
    
    # Запуск тестов TypeScript клиента
    echo "Running TypeScript Client tests..."
    cd "${PROJECT_ROOT}/src/typescript_client"
    npm test
    
    # Запуск тестов C++ физического движка
    echo "Running C++ Physics Engine tests..."
    cd "${PROJECT_ROOT}/src/cpp_physics"
    cd build
    ctest
    
    # Запуск тестов Python инструментов
    echo "Running Python Tools tests..."
    cd "${PROJECT_ROOT}/src/python_tools"
    python -m pytest tests/
    
    echo -e "${GREEN}All tests passed.${NC}"
}

# Основная функция сборки
main() {
    echo -e "${BLUE}Starting build process for Tetris Towers...${NC}"
    
    # Определение платформы
    detect_platform
    
    # Проверка зависимостей
    check_dependencies
    
    # Сборка компонентов
    build_python_server
    build_python_analytics
    build_python_ai
    build_typescript_client
    build_cpp_physics
    build_python_tools
    
    # Создание конфигурационных файлов и скриптов запуска
    create_config_files
    create_launch_scripts
    create_documentation
    
    # Запуск тестов
    run_tests
    
    # Создание архива
    create_archive
    
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}The game can be found in the '${DIST_DIR}' directory.${NC}"
    echo -e "${GREEN}To start the game, run 'start.sh' (Linux/macOS) or 'start.bat' (Windows) in the distribution directory.${NC}"
}

# Обработка аргументов командной строки
RUN_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-tests)
            RUN_TESTS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --with-tests    Run tests after building"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Запуск основной функции
main

