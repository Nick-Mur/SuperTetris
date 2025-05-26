@echo off
setlocal enabledelayedexpansion

:: Скрипт запуска для Tetris с элементами Tricky Towers на Windows

:: Определение цветов для вывода
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Определение корневой директории проекта
set "PROJECT_ROOT=%~dp0"
set "DIST_DIR=%PROJECT_ROOT%dist"
set "LOG_DIR=%PROJECT_ROOT%logs"

:: Создание необходимых директорий
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Запуск C++ физического движка
echo %BLUE%Starting C++ Physics Engine...%NC%
start /B "%DIST_DIR%\bin\physics_engine.exe" > "%LOG_DIR%\physics_engine.log" 2>&1
echo %GREEN%C++ Physics Engine started.%NC%

:: Запуск Rust серверной части
echo %BLUE%Starting Rust Game Server...%NC%
start /B "%DIST_DIR%\bin\tetris_server.exe" --config "%PROJECT_ROOT%config\server.toml" > "%LOG_DIR%\rust_server.log" 2>&1
echo %GREEN%Rust Game Server started.%NC%

:: Запуск Python игровой логики
echo %BLUE%Starting Python Game Logic...%NC%
cd /D "%DIST_DIR%\python"
start /B python main.py > "%LOG_DIR%\python_logic.log" 2>&1
echo %GREEN%Python Game Logic started.%NC%

:: Запуск TypeScript клиентской части
echo %BLUE%Starting TypeScript Client...%NC%
cd /D "%DIST_DIR%\client"
start /B npm start > "%LOG_DIR%\typescript_client.log" 2>&1
echo %GREEN%TypeScript Client started.%NC%

:: Запуск Julia ИИ системы
echo %BLUE%Starting Julia AI System...%NC%
cd /D "%DIST_DIR%\julia"
start /B julia main.jl > "%LOG_DIR%\julia_ai.log" 2>&1
echo %GREEN%Julia AI System started.%NC%

:: Запуск Go инструментов разработки
echo %BLUE%Starting Go Development Tools...%NC%
start /B "%DIST_DIR%\bin\dev_tools.exe" > "%LOG_DIR%\go_tools.log" 2>&1
echo %GREEN%Go Development Tools started.%NC%

:: Запуск Scala аналитики
echo %BLUE%Starting Scala Analytics...%NC%
cd /D "%DIST_DIR%\scala"
start /B sbt run > "%LOG_DIR%\scala_analytics.log" 2>&1
echo %GREEN%Scala Analytics started.%NC%

echo %GREEN%All components started successfully.%NC%
echo %YELLOW%Press Ctrl+C to stop all components.%NC%

:: Ожидание завершения
pause

:: Остановка всех процессов
echo %YELLOW%Shutting down all components...%NC%
taskkill /F /IM physics_engine.exe /T 2>nul
taskkill /F /IM tetris_server.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM julia.exe /T 2>nul
taskkill /F /IM dev_tools.exe /T 2>nul
taskkill /F /IM java.exe /T 2>nul

echo %GREEN%All components stopped.%NC% 