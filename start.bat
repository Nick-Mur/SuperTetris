@echo off
setlocal enabledelayedexpansion

:: Скрипт запуска для Tetris с элементами Tricky Towers на Windows

:: Цвета для вывода
set "RED=[91m"
set "GREEN=[92m"
set "BLUE=[94m"
set "NC=[0m"

:: Пути
set "PROJECT_ROOT=%~dp0"
set "DIST_DIR=%PROJECT_ROOT%dist"
set "LOG_DIR=%PROJECT_ROOT%logs"

:: Создание директории для логов
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Запуск Python серверной части
echo %BLUE%Starting Python Game Server...%NC%
cd /D "%PROJECT_ROOT%src\python_server"
start /B python src\main.py > "%LOG_DIR%\python_server.log" 2>&1
echo %GREEN%Python Game Server started.%NC%

:: Запуск Python аналитики
echo %BLUE%Starting Python Analytics...%NC%
cd /D "%PROJECT_ROOT%src\python_analytics"
start /B python src\main.py > "%LOG_DIR%\python_analytics.log" 2>&1
echo %GREEN%Python Analytics started.%NC%

:: Запуск Python ИИ
echo %BLUE%Starting Python AI...%NC%
cd /D "%PROJECT_ROOT%src\python_ai"
start /B python src\main.py > "%LOG_DIR%\python_ai.log" 2>&1
echo %GREEN%Python AI started.%NC%

:: Запуск TypeScript клиента
echo %BLUE%Starting TypeScript Client...%NC%
cd /D "%PROJECT_ROOT%src\typescript_client"
start /B npm start > "%LOG_DIR%\typescript_client.log" 2>&1
echo %GREEN%TypeScript Client started.%NC%

:: Запуск C++ физического движка
echo %BLUE%Starting C++ Physics Engine...%NC%
cd /D "%PROJECT_ROOT%src\cpp_physics\build"
start /B physics_engine.exe > "%LOG_DIR%\cpp_physics.log" 2>&1
echo %GREEN%C++ Physics Engine started.%NC%

:: Запуск Go инструментов
echo %BLUE%Starting Go Development Tools...%NC%
cd /D "%PROJECT_ROOT%src\go_tools"
start /B dev_tools.exe > "%LOG_DIR%\go_tools.log" 2>&1
echo %GREEN%Go Development Tools started.%NC%

echo %GREEN%All components started successfully!%NC%
echo Open http://localhost:3000 in your browser to play the game.

:: Ожидание нажатия Ctrl+C для завершения
pause > nul 