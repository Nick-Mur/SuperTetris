#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import webbrowser
import time
import signal
import atexit
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tetris_launcher.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TetrisLauncher")

# Определение текущей директории
if getattr(sys, 'frozen', False):
    # Если запущено как исполняемый файл
    current_dir = Path(os.path.dirname(sys.executable))
else:
    # Если запущено как скрипт
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

# Определение путей к исполняемым файлам в зависимости от ОС
is_windows = platform.system() == "Windows"
bin_ext = ".exe" if is_windows else ""

# Поиск бинарных файлов в нескольких возможных местах
possible_bin_dirs = [
    current_dir / "bin",
    current_dir.parent / "bin",
    current_dir.parent / "build" / "bin",
    Path("/home/ubuntu/tetris_project/build/bin")
]

bin_dir = None
for dir_path in possible_bin_dirs:
    if dir_path.exists():
        bin_dir = dir_path
        break

if bin_dir is None:
    # Если директория с бинарными файлами не найдена, используем текущую директорию
    bin_dir = current_dir
    logger.warning(f"Директория с бинарными файлами не найдена, используем {bin_dir}")

# Аналогично для библиотек
possible_lib_dirs = [
    current_dir / "lib",
    current_dir.parent / "lib",
    current_dir.parent / "build" / "lib",
    Path("/home/ubuntu/tetris_project/build/lib")
]

lib_dir = None
for dir_path in possible_lib_dirs:
    if dir_path.exists():
        lib_dir = dir_path
        break

if lib_dir is None:
    # Если директория с библиотеками не найдена, используем текущую директорию
    lib_dir = current_dir
    logger.warning(f"Директория с библиотеками не найдена, используем {lib_dir}")

# Пути к исполняемым файлам
physics_engine_path = bin_dir / f"physics_engine{bin_ext}"
game_server_path = bin_dir / f"game_server{bin_ext}"
ai_system_path = bin_dir / f"ai_system{bin_ext}"
analytics_jar_path = lib_dir / "analytics-assembly-1.0.jar"

# Список процессов для отслеживания
processes = []

def start_process(cmd, name):
    """Запуск процесса и добавление его в список для отслеживания"""
    logger.info(f"Запуск {name}: {' '.join(cmd)}")
    
    try:
        if is_windows:
            # На Windows используем CREATE_NEW_CONSOLE для отдельных окон
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # На Unix-подобных системах перенаправляем вывод в файлы
            log_file = open(f"{name}.log", "w")
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
        
        processes.append((process, name))
        logger.info(f"{name} запущен с PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Ошибка при запуске {name}: {e}")
        return None

def cleanup():
    """Завершение всех запущенных процессов"""
    logger.info("Завершение всех процессов...")
    
    for process, name in processes:
        try:
            if process.poll() is None:  # Если процесс еще работает
                logger.info(f"Завершение {name} (PID {process.pid})")
                if is_windows:
                    process.terminate()
                else:
                    process.send_signal(signal.SIGTERM)
                
                # Даем процессу время на корректное завершение
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} не завершился корректно, принудительное завершение")
                    process.kill()
        except Exception as e:
            logger.error(f"Ошибка при завершении {name}: {e}")
    
    logger.info("Все процессы завершены")

def check_java():
    """Проверка наличия Java"""
    try:
        subprocess.run(
            ["java", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return True
    except:
        return False

def main():
    """Основная функция запуска игры"""
    logger.info("Запуск Tetris с элементами Tricky Towers")
    
    # Регистрация функции очистки при выходе
    atexit.register(cleanup)
    
    # Проверка наличия необходимых файлов
    missing_files = []
    for path in [physics_engine_path, game_server_path, ai_system_path]:
        if not path.exists():
            missing_files.append(str(path))
    
    if missing_files:
        logger.error(f"Отсутствуют необходимые файлы: {', '.join(missing_files)}")
        print(f"Ошибка: отсутствуют необходимые файлы: {', '.join(missing_files)}")
        print("Пожалуйста, убедитесь, что игра была корректно установлена.")
        
        # В тестовом режиме не запрашиваем ввод и создаем заглушки
        if os.environ.get('TETRIS_TEST_MODE') == '1':
            logger.info("Запуск в тестовом режиме, создание заглушек...")
            
            # Создание директорий для заглушек
            os.makedirs(os.path.dirname(physics_engine_path), exist_ok=True)
            
            # Создание заглушек
            for path in [physics_engine_path, game_server_path, ai_system_path]:
                if not path.exists():
                    with open(path, 'w') as f:
                        f.write('#!/bin/bash\necho "Mock binary running"\nwhile true; do sleep 1; done\n')
                    os.chmod(path, 0o755)
                    logger.info(f"Создана заглушка: {path}")
        else:
            try:
                input("Нажмите Enter для выхода...")
            except (EOFError, KeyboardInterrupt):
                pass
            return 1
    
    # Проверка наличия Java для запуска аналитики
    if not check_java():
        logger.warning("Java не найдена. Система аналитики не будет запущена.")
        print("Предупреждение: Java не найдена. Система аналитики не будет запущена.")
        print("Для полной функциональности установите Java Runtime Environment.")
    
    # Запуск физического движка
    physics_process = start_process(
        [str(physics_engine_path)],
        "Физический движок"
    )
    
    # Запуск серверной части
    server_process = start_process(
        [str(game_server_path)],
        "Игровой сервер"
    )
    
    # Запуск системы ИИ
    ai_process = start_process(
        [str(ai_system_path)],
        "Система ИИ"
    )
    
    # Запуск системы аналитики, если есть Java
    if check_java() and analytics_jar_path.exists():
        analytics_process = start_process(
            ["java", "-jar", str(analytics_jar_path)],
            "Система аналитики"
        )
    
    # Ожидание запуска всех сервисов
    logger.info("Ожидание запуска всех сервисов...")
    time.sleep(2)
    
    # Открытие игры в браузере (только если не в тестовом режиме)
    if os.environ.get('TETRIS_TEST_MODE') != '1':
        logger.info("Открытие игры в браузере...")
        try:
            webbrowser.open("http://localhost:3000")
        except Exception as e:
            logger.error(f"Не удалось открыть браузер: {e}")
    
        print("\nИгра Tetris с элементами Tricky Towers запущена!")
        print("Игра открыта в вашем браузере.")
        print("Это окно можно свернуть, но не закрывайте его до завершения игры.")
        print("\nДля завершения игры нажмите Ctrl+C в этом окне или закройте его.")
    else:
        logger.info("Тестовый режим: пропуск открытия браузера")
        # В тестовом режиме выходим через 5 секунд
        time.sleep(5)
        return 0
    
    try:
        # Ожидание завершения всех процессов или прерывания пользователем
        while True:
            # Проверка состояния процессов
            all_running = True
            for process, name in processes:
                if process.poll() is not None:  # Если процесс завершился
                    logger.warning(f"{name} неожиданно завершился с кодом {process.returncode}")
                    all_running = False
            
            if not all_running:
                logger.warning("Один или несколько процессов неожиданно завершились")
                print("\nВнимание: один или несколько компонентов игры неожиданно завершились.")
                print("Игра может работать некорректно. Рекомендуется перезапустить игру.")
            
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершение работы...")
        print("\nЗавершение игры...")
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
