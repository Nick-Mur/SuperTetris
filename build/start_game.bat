@echo off
echo Запуск игры Tetris с элементами Tricky Towers...

REM Запуск физического движка
start bin\physics_engine.exe

REM Запуск серверной части
start bin\game_server.exe

REM Запуск системы ИИ
start bin\ai_system.exe

REM Запуск системы аналитики
start javaw -jar lib\analytics-assembly-1.0.jar

REM Открытие игры в браузере
timeout /t 2
start http://localhost:3000

echo Игра запущена. Закройте это окно для завершения всех процессов.
pause
taskkill /F /IM physics_engine.exe
taskkill /F /IM game_server.exe
taskkill /F /IM ai_system.exe
taskkill /F /IM javaw.exe
