#!/usr/bin/env python3

import os
import sys
import json
import requests
import time
import websocket
import threading
import queue
import random

# Функция для проверки интеграции между C++ и Rust
def test_cpp_rust_integration():
    print("Testing C++ Physics Engine and Rust Server integration...")
    
    try:
        # Проверка API сервера для физических операций
        response = requests.post(
            "http://localhost:8080/api/v1/physics/simulate",
            json={"dt": 0.016, "entities": [{"id": 1, "type": "block", "x": 5, "y": 0, "rotation": 0}]}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        result = response.json()
        if "entities" not in result or not isinstance(result["entities"], list):
            print("Error: Invalid response format")
            return False
        
        print("C++ Physics Engine and Rust Server integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для проверки интеграции между Rust и Python
def test_rust_python_integration():
    print("Testing Rust Server and Python Game Logic integration...")
    
    try:
        # Создание новой игры
        response = requests.post(
            "http://localhost:8080/api/v1/games",
            json={"mode": "RACE", "players": 1, "difficulty": "EASY"}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_data = response.json()
        if "gameId" not in game_data:
            print("Error: Invalid response format (missing gameId)")
            return False
        
        game_id = game_data["gameId"]
        
        # Выполнение действия в игре
        response = requests.post(
            f"http://localhost:8080/api/v1/games/{game_id}/action",
            json={"playerId": "player1", "actionType": "MOVE_LEFT"}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        # Получение состояния игры
        response = requests.get(f"http://localhost:8080/api/v1/games/{game_id}")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_state = response.json()
        if "state" not in game_state:
            print("Error: Invalid response format (missing state)")
            return False
        
        print("Rust Server and Python Game Logic integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для проверки интеграции между Python и TypeScript
def test_python_typescript_integration():
    print("Testing Python Game Logic and TypeScript Client integration...")
    
    message_queue = queue.Queue()
    
    def on_message(ws, message):
        message_queue.put(json.loads(message))
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(ws):
        print("WebSocket connection opened")
        ws.send(json.dumps({
            "type": "JOIN_GAME",
            "gameId": game_id,
            "playerId": "player1"
        }))
    
    try:
        # Создание новой игры
        response = requests.post(
            "http://localhost:8080/api/v1/games",
            json={"mode": "RACE", "players": 1, "difficulty": "EASY"}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_data = response.json()
        if "gameId" not in game_data:
            print("Error: Invalid response format (missing gameId)")
            return False
        
        game_id = game_data["gameId"]
        
        # Подключение к WebSocket
        ws = websocket.WebSocketApp(
            f"ws://localhost:8081/ws",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Ожидание подключения
        time.sleep(2)
        
        # Выполнение действия в игре через WebSocket
        ws.send(json.dumps({
            "type": "PLAYER_ACTION",
            "gameId": game_id,
            "playerId": "player1",
            "actionType": "MOVE_RIGHT"
        }))
        
        # Ожидание ответа
        try:
            message = message_queue.get(timeout=5)
            if message.get("type") != "GAME_STATE_UPDATE":
                print(f"Error: Unexpected message type: {message.get('type')}")
                return False
        except queue.Empty:
            print("Error: No response received from WebSocket")
            return False
        
        # Закрытие WebSocket
        ws.close()
        
        print("Python Game Logic and TypeScript Client integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для проверки интеграции между Rust и Julia
def test_rust_julia_integration():
    print("Testing Rust Server and Julia AI integration...")
    
    try:
        # Создание новой игры с ИИ
        response = requests.post(
            "http://localhost:8080/api/v1/games",
            json={"mode": "RACE", "players": 1, "ai_opponents": 1, "difficulty": "EASY"}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_data = response.json()
        if "gameId" not in game_data:
            print("Error: Invalid response format (missing gameId)")
            return False
        
        game_id = game_data["gameId"]
        
        # Ожидание действий ИИ
        time.sleep(5)
        
        # Получение состояния игры
        response = requests.get(f"http://localhost:8080/api/v1/games/{game_id}")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_state = response.json()
        
        # Проверка наличия действий ИИ
        if "ai_actions" not in game_state or len(game_state["ai_actions"]) == 0:
            print("Error: No AI actions recorded")
            return False
        
        print("Rust Server and Julia AI integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для проверки интеграции между Go и Rust
def test_go_rust_integration():
    print("Testing Go Tools and Rust Server integration...")
    
    try:
        # Проверка API для инструментов разработки
        response = requests.get("http://localhost:8080/api/v1/dev/status")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        status = response.json()
        if "status" not in status or status["status"] != "ok":
            print("Error: Invalid status response")
            return False
        
        # Создание тестового уровня
        response = requests.post(
            "http://localhost:8080/api/v1/dev/levels",
            json={
                "name": "Test Level",
                "difficulty": "MEDIUM",
                "blocks": [
                    {"type": "L", "initialX": 5, "initialY": 0},
                    {"type": "I", "initialX": 2, "initialY": 3}
                ]
            }
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        level_data = response.json()
        if "levelId" not in level_data:
            print("Error: Invalid response format (missing levelId)")
            return False
        
        level_id = level_data["levelId"]
        
        # Получение созданного уровня
        response = requests.get(f"http://localhost:8080/api/v1/dev/levels/{level_id}")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        level = response.json()
        if "name" not in level or level["name"] != "Test Level":
            print("Error: Invalid level data")
            return False
        
        print("Go Tools and Rust Server integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для проверки интеграции между Scala и Rust
def test_scala_rust_integration():
    print("Testing Scala Analytics and Rust Server integration...")
    
    try:
        # Создание нескольких игр для генерации данных аналитики
        for i in range(3):
            response = requests.post(
                "http://localhost:8080/api/v1/games",
                json={"mode": "RACE", "players": 1, "difficulty": "EASY"}
            )
            
            if response.status_code != 200:
                print(f"Error: Server returned status code {response.status_code}")
                return False
            
            game_id = response.json()["gameId"]
            
            # Выполнение нескольких действий
            for action in ["MOVE_LEFT", "MOVE_RIGHT", "ROTATE_CW", "HARD_DROP"]:
                response = requests.post(
                    f"http://localhost:8080/api/v1/games/{game_id}/action",
                    json={"playerId": "player1", "actionType": action}
                )
            
            # Завершение игры
            response = requests.post(
                f"http://localhost:8080/api/v1/games/{game_id}/end",
                json={"playerId": "player1", "score": 1000 * (i + 1)}
            )
        
        # Ожидание обработки данных аналитикой
        time.sleep(5)
        
        # Получение аналитических данных
        response = requests.get("http://localhost:8080/api/v1/analytics/summary")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        analytics = response.json()
        if "gameCount" not in analytics or analytics["gameCount"] < 3:
            print("Error: Analytics data not properly collected")
            return False
        
        print("Scala Analytics and Rust Server integration test passed.")
        return True
    
    except Exception as e:
        print(f"Error during test: {e}")
        return False

# Функция для полного системного теста
def test_full_system():
    print("Running full system test...")
    
    message_queue = queue.Queue()
    
    def on_message(ws, message):
        message_queue.put(json.loads(message))
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(ws):
        print("WebSocket connection opened")
        ws.send(json.dumps({
            "type": "JOIN_GAME",
            "gameId": game_id,
            "playerId": "player1"
        }))
    
    try:
        # 1. Проверка доступности сервера
        response = requests.get("http://localhost:8080/api/v1/status")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        # 2. Создание новой игры
        response = requests.post(
            "http://localhost:8080/api/v1/games",
            json={"mode": "RACE", "players": 1, "ai_opponents": 1, "difficulty": "MEDIUM"}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        game_data = response.json()
        game_id = game_data["gameId"]
        
        # 3. Подключение к WebSocket
        ws = websocket.WebSocketApp(
            f"ws://localhost:8081/ws",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Ожидание подключения
        time.sleep(2)
        
        # 4. Симуляция игрового процесса
        actions = ["MOVE_LEFT", "MOVE_RIGHT", "ROTATE_CW", "ROTATE_CCW", "HARD_DROP"]
        
        for i in range(20):
            # Выбор случайного действия
            action = random.choice(actions)
            
            # Отправка действия через WebSocket
            ws.send(json.dumps({
                "type": "PLAYER_ACTION",
                "gameId": game_id,
                "playerId": "player1",
                "actionType": action
            }))
            
            # Ожидание обновления состояния
            try:
                message = message_queue.get(timeout=2)
                if message.get("type") != "GAME_STATE_UPDATE":
                    print(f"Warning: Unexpected message type: {message.get('type')}")
            except queue.Empty:
                print("Warning: No response received from WebSocket")
            
            # Небольшая пауза между действиями
            time.sleep(0.5)
        
        # 5. Использование заклинания
        ws.send(json.dumps({
            "type": "PLAYER_ACTION",
            "gameId": game_id,
            "playerId": "player1",
            "actionType": "CAST_SPELL",
            "spellType": "FREEZE"
        }))
        
        # Ожидание обновления состояния
        try:
            message = message_queue.get(timeout=2)
        except queue.Empty:
            print("Warning: No response received after spell cast")
        
        # 6. Завершение игры
        response = requests.post(
            f"http://localhost:8080/api/v1/games/{game_id}/end",
            json={"playerId": "player1", "score": 5000}
        )
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        # 7. Получение аналитических данных
        time.sleep(2)  # Ожидание обработки данных
        
        response = requests.get("http://localhost:8080/api/v1/analytics/games")
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return False
        
        analytics = response.json()
        if "games" not in analytics:
            print("Error: Invalid analytics response")
            return False
        
        # 8. Закрытие WebSocket
        ws.close()
        
        print("Full system test passed successfully.")
        return True
    
    except Exception as e:
        print(f"Error during full system test: {e}")
        return False

# Основная функция
def main():
    print("Starting integration tests...")
    
    # Запуск тестов интеграции
    tests = [
        test_cpp_rust_integration,
        test_rust_python_integration,
        test_python_typescript_integration,
        test_rust_julia_integration,
        test_go_rust_integration,
        test_scala_rust_integration,
        test_full_system
    ]
    
    success = True
    for test in tests:
        if not test():
            success = False
            break
    
    if success:
        print("All integration tests passed successfully.")
        return 0
    else:
        print("Integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
