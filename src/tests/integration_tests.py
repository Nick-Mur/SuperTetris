import unittest
import json
import requests
import subprocess
import time
import os
import signal
import sys
from multiprocessing import Process

# Добавление пути к исходным файлам
sys.path.append('../python_logic')

# Импорт модулей для тестирования
from game_logic import GameLogic, TetrominoType, GameMode

class TestTetrisIntegration(unittest.TestCase):
    """
    Интеграционные тесты для проверки взаимодействия между компонентами игры
    """
    
    @classmethod
    def setUpClass(cls):
        """Запуск всех необходимых сервисов перед тестированием"""
        print("Starting test services...")
        
        # Проверка наличия необходимых директорий
        required_dirs = [
            "../cpp_physics/build",
            "../python_logic"
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                raise RuntimeError(f"Required directory not found: {directory}")
        
        # Запуск физического движка (C++)
        try:
            cls.physics_process = subprocess.Popen(
                ["./physics_engine"],
                cwd="../cpp_physics/build",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            raise RuntimeError(f"Failed to start physics engine: {e}")
        
        # Запуск Python сервера
        try:
            cls.server_process = subprocess.Popen(
                ["python", "server.py"],
                cwd="../python_logic",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            # Остановка физического движка в случае ошибки
            cls.physics_process.terminate()
            raise RuntimeError(f"Failed to start Python server: {e}")
        
        # Ожидание запуска всех сервисов
        max_retries = 30
        retry_interval = 1
        
        for i in range(max_retries):
            try:
                # Проверка физического движка
                physics_response = requests.get("http://localhost:9000/physics/status")
                if physics_response.status_code != 200:
                    raise requests.RequestException("Physics engine not ready")
                
                # Проверка Python сервера
                server_response = requests.get("http://localhost:8000/health")
                if server_response.status_code != 200:
                    raise requests.RequestException("Python server not ready")
                
                # Если оба сервиса доступны, выходим из цикла
                break
                
            except requests.RequestException:
                if i == max_retries - 1:
                    # Остановка процессов в случае таймаута
                    cls.tearDownClass()
                    raise RuntimeError("Services failed to start within timeout")
                time.sleep(retry_interval)
        
        # Базовый URL для API
        cls.base_url = "http://localhost:8000"
    
    @classmethod
    def tearDownClass(cls):
        """Остановка всех сервисов после тестирования"""
        print("Stopping test services...")
        
        # Остановка процессов
        for process in [cls.physics_process, cls.server_process]:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
    
    def test_01_server_health(self):
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
        except requests.RequestException as e:
            self.fail(f"Server health check failed: {e}")
    
    def test_02_game_creation(self):
        """Проверка создания новой игры"""
        payload = {
            "mode": "RACE",
            "player_name": "TestPlayer",
            "difficulty": "medium"
        }
        
        try:
            response = requests.post(f"{self.base_url}/game/start", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("player_id", data)
            self.assertIn("session_id", data)
            
            # Сохранение ID игрока и сессии для последующих тестов
            self.__class__.player_id = data["player_id"]
            self.__class__.session_id = data["session_id"]
        except requests.RequestException as e:
            self.fail(f"Game creation failed: {e}")
    
    def test_03_game_state(self):
        """Проверка получения состояния игры"""
        try:
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Проверка структуры данных
            self.assertIn("players", data)
            self.assertIn("gameMode", data)
            self.assertIn("currentTurn", data)
            self.assertIn("gameStatus", data)
            self.assertIn("timer", data)
            
            # Проверка данных игрока
            player_key = str(self.player_id)
            self.assertIn(player_key, data["players"])
            player = data["players"][player_key]
            
            self.assertEqual(player["name"], "TestPlayer")
            self.assertEqual(player["health"], 3)
            self.assertGreaterEqual(len(player["towerBlocks"]), 0)
            
            # Проверка режима игры
            self.assertEqual(data["gameMode"], "RACE")
        except requests.RequestException as e:
            self.fail(f"Game state retrieval failed: {e}")
    
    def test_04_tetromino_movement(self):
        """Проверка движения тетромино"""
        # Получение текущего состояния
        response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
        data = response.json()
        player_key = str(self.player_id)
        
        # Проверка наличия текущего тетромино
        self.assertIn("currentTetromino", data["players"][player_key])
        current_tetromino = data["players"][player_key]["currentTetromino"]
        
        if current_tetromino is None:
            self.skipTest("No current tetromino available")
        
        # Запоминание начальной позиции
        initial_x = current_tetromino["x"]
        
        # Отправка команды движения вправо
        move_payload = {
            "player_id": self.player_id,
            "move_type": "move_right",
            "x": initial_x + 1,
            "y": current_tetromino["y"],
            "rotation": current_tetromino["rotation"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/game/{self.session_id}/move", json=move_payload)
            self.assertEqual(response.status_code, 200)
            
            # Проверка обновления позиции
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            data = response.json()
            updated_tetromino = data["players"][player_key]["currentTetromino"]
            
            # Проверка, что X-координата увеличилась
            self.assertEqual(updated_tetromino["x"], initial_x + 1)
        except requests.RequestException as e:
            self.fail(f"Tetromino movement failed: {e}")
    
    def test_05_tetromino_rotation(self):
        """Проверка вращения тетромино"""
        # Получение текущего состояния
        response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
        data = response.json()
        player_key = str(self.player_id)
        
        # Проверка наличия текущего тетромино
        self.assertIn("currentTetromino", data["players"][player_key])
        current_tetromino = data["players"][player_key]["currentTetromino"]
        
        if current_tetromino is None:
            self.skipTest("No current tetromino available")
        
        # Запоминание начального вращения
        initial_rotation = current_tetromino["rotation"]
        
        # Отправка команды вращения
        rotate_payload = {
            "player_id": self.player_id,
            "move_type": "rotate",
            "x": current_tetromino["x"],
            "y": current_tetromino["y"],
            "rotation": (initial_rotation + 90) % 360
        }
        
        try:
            response = requests.post(f"{self.base_url}/game/{self.session_id}/move", json=rotate_payload)
            self.assertEqual(response.status_code, 200)
            
            # Проверка обновления вращения
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            data = response.json()
            updated_tetromino = data["players"][player_key]["currentTetromino"]
            
            # Проверка, что вращение изменилось
            self.assertEqual(updated_tetromino["rotation"], (initial_rotation + 90) % 360)
        except requests.RequestException as e:
            self.fail(f"Tetromino rotation failed: {e}")
    
    def test_06_tetromino_drop(self):
        """Проверка сброса тетромино"""
        # Получение текущего состояния
        response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
        data = response.json()
        player_key = str(self.player_id)
        
        # Проверка наличия текущего тетромино
        self.assertIn("currentTetromino", data["players"][player_key])
        current_tetromino = data["players"][player_key]["currentTetromino"]
        
        if current_tetromino is None:
            self.skipTest("No current tetromino available")
        
        # Запоминание количества блоков в башне
        initial_blocks_count = len(data["players"][player_key]["towerBlocks"])
        
        # Отправка команды сброса
        drop_payload = {
            "player_id": self.player_id,
            "move_type": "drop",
            "x": current_tetromino["x"],
            "y": current_tetromino["y"],
            "rotation": current_tetromino["rotation"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/game/{self.session_id}/move", json=drop_payload)
            self.assertEqual(response.status_code, 200)
            
            # Проверка обновления состояния
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            data = response.json()
            
            # Проверка, что количество блоков увеличилось
            updated_blocks_count = len(data["players"][player_key]["towerBlocks"])
            self.assertGreater(updated_blocks_count, initial_blocks_count)
            
            # Проверка, что появилось новое тетромино
            self.assertIsNotNone(data["players"][player_key]["currentTetromino"])
        except requests.RequestException as e:
            self.fail(f"Tetromino drop failed: {e}")
    
    def test_07_spell_casting(self):
        """Проверка использования заклинаний"""
        # Получение текущего состояния
        response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
        data = response.json()
        player_key = str(self.player_id)
        
        # Проверка наличия заклинаний
        self.assertIn("spells", data["players"][player_key])
        spells = data["players"][player_key]["spells"]
        
        if not spells:
            self.skipTest("No spells available")
        
        # Выбор первого заклинания
        spell = spells[0]
        
        # Отправка команды использования заклинания
        spell_payload = {
            "player_id": self.player_id,
            "spell_type": spell,
            "target_id": self.player_id  # Использование на себя
        }
        
        try:
            response = requests.post(f"{self.base_url}/game/{self.session_id}/spell", json=spell_payload)
            self.assertEqual(response.status_code, 200)
            
            # Проверка обновления состояния
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            data = response.json()
            
            # Проверка, что заклинание исчезло из списка
            updated_spells = data["players"][player_key]["spells"]
            self.assertNotIn(spell, updated_spells)
        except requests.RequestException as e:
            self.fail(f"Spell casting failed: {e}")
    
    def test_08_physics_simulation(self):
        """Проверка физической симуляции"""
        # Создание тестового блока
        block_payload = {
            "x": 5.0,
            "y": 10.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        try:
            response = requests.post("http://localhost:9000/physics/add_block", json=block_payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("block_id", data)
            
            # Запуск симуляции на один шаг
            sim_payload = {
                "time_step": 0.016  # ~60 FPS
            }
            response = requests.post("http://localhost:9000/physics/step", json=sim_payload)
            self.assertEqual(response.status_code, 200)
            
            # Получение состояния блоков
            response = requests.get("http://localhost:9000/physics/blocks")
            self.assertEqual(response.status_code, 200)
            blocks = response.json()["blocks"]
            
            # Проверка, что блок существует и его Y-координата увеличилась (падение)
            block = next((b for b in blocks if b["id"] == data["block_id"]), None)
            self.assertIsNotNone(block)
            self.assertGreater(block["y"], 10.0)
        except requests.RequestException as e:
            self.fail(f"Physics simulation failed: {e}")
    
    def test_09_analytics_data(self):
        """Проверка сбора аналитических данных"""
        try:
            # Отправка тестового события
            event_payload = {
                "session_id": self.session_id,
                "event_type": "TEST_EVENT",
                "player_id": self.player_id,
                "data": {
                    "test_key": "test_value"
                }
            }
            
            response = requests.post(f"{self.base_url}/analytics/event", json=event_payload)
            self.assertEqual(response.status_code, 200)
            
            # Получение аналитики по сессии
            response = requests.get(f"{self.base_url}/analytics/session/{self.session_id}")
            self.assertEqual(response.status_code, 200)
            
            # Проверка наличия события в аналитике
            data = response.json()
            self.assertIn("events", data)
            
            # Поиск нашего тестового события
            test_event = next((e for e in data["events"] if e["event_type"] == "TEST_EVENT"), None)
            self.assertIsNotNone(test_event)
            self.assertEqual(test_event["player_id"], self.player_id)
            self.assertEqual(test_event["data"]["test_key"], "test_value")
        except requests.RequestException as e:
            self.fail(f"Analytics data collection failed: {e}")
    
    def test_10_end_game(self):
        """Проверка завершения игры"""
        try:
            response = requests.post(f"{self.base_url}/game/{self.session_id}/end")
            self.assertEqual(response.status_code, 200)
            
            # Проверка обновления состояния
            response = requests.get(f"{self.base_url}/game/{self.session_id}/state")
            data = response.json()
            
            # Проверка, что игра завершена
            self.assertEqual(data["gameStatus"], "FINISHED")
        except requests.RequestException as e:
            self.fail(f"Game ending failed: {e}")


class TestPythonGameLogic(unittest.TestCase):
    """
    Модульные тесты для проверки логики игры на Python
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.game_logic = GameLogic()
    
    def test_01_tetromino_generation(self):
        """Проверка генерации тетромино"""
        tetromino = self.game_logic.generate_tetromino()
        
        # Проверка структуры тетромино
        self.assertIn("type", tetromino)
        self.assertIn("x", tetromino)
        self.assertIn("y", tetromino)
        self.assertIn("rotation", tetromino)
        
        # Проверка типа тетромино
        self.assertIn(tetromino["type"], [t.value for t in TetrominoType])
        
        # Проверка начальной позиции
        self.assertEqual(tetromino["y"], 0)
        self.assertGreaterEqual(tetromino["x"], 0)
        self.assertLess(tetromino["x"], 10)
    
    def test_02_collision_detection(self):
        """Проверка обнаружения коллизий"""
        # Создание тестового состояния игры
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": [
                {"id": 1, "x": 5, "y": 19, "width": 1, "height": 1}
            ]
        }
        
        # Проверка коллизии с блоком
        self.assertTrue(self.game_logic.check_collision(game_state, 5, 19, TetrominoType.I, 0))
        
        # Проверка коллизии с границами поля
        self.assertTrue(self.game_logic.check_collision(game_state, -1, 0, TetrominoType.I, 0))
        self.assertTrue(self.game_logic.check_collision(game_state, 10, 0, TetrominoType.I, 0))
        self.assertTrue(self.game_logic.check_collision(game_state, 0, 20, TetrominoType.I, 0))
        
        # Проверка отсутствия коллизии
        self.assertFalse(self.game_logic.check_collision(game_state, 0, 0, TetrominoType.I, 0))
    
    def test_03_tetromino_placement(self):
        """Проверка размещения тетромино"""
        # Создание тестового состояния игры
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": []
        }
        
        # Размещение тетромино
        tetromino = {
            "type": TetrominoType.I.value,
            "x": 5,
            "y": 18,
            "rotation": 0
        }
        
        updated_state = self.game_logic.place_tetromino(game_state, tetromino)
        
        # Проверка, что блоки добавлены в башню
        self.assertEqual(len(updated_state["tower_blocks"]), 4)  # I-тетромино состоит из 4 блоков
        
        # Проверка позиций блоков
        for block in updated_state["tower_blocks"]:
            self.assertGreaterEqual(block["x"], 5)
            self.assertLess(block["x"], 9)
            self.assertEqual(block["y"], 18)
    
    def test_04_line_clearing(self):
        """Проверка очистки заполненных линий"""
        # Создание тестового состояния игры с заполненной нижней линией
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": [
                {"id": i, "x": i, "y": 19, "width": 1, "height": 1} for i in range(10)
            ]
        }
        
        updated_state = self.game_logic.check_and_clear_lines(game_state)
        
        # Проверка, что линия очищена
        self.assertEqual(len(updated_state["tower_blocks"]), 0)
        
        # Создание тестового состояния с частично заполненной линией
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": [
                {"id": i, "x": i, "y": 19, "width": 1, "height": 1} for i in range(9)
            ]
        }
        
        updated_state = self.game_logic.check_and_clear_lines(game_state)
        
        # Проверка, что линия не очищена
        self.assertEqual(len(updated_state["tower_blocks"]), 9)
    
    def test_05_score_calculation(self):
        """Проверка расчета очков"""
        # Начальное состояние
        player_state = {
            "score": 0,
            "lines_cleared": 0
        }
        
        # Очистка одной линии
        updated_state = self.game_logic.update_score(player_state, 1)
        self.assertEqual(updated_state["score"], 100)
        self.assertEqual(updated_state["lines_cleared"], 1)
        
        # Очистка двух линий
        updated_state = self.game_logic.update_score(updated_state, 2)
        self.assertEqual(updated_state["score"], 100 + 300)
        self.assertEqual(updated_state["lines_cleared"], 3)
        
        # Очистка трех линий
        updated_state = self.game_logic.update_score(updated_state, 3)
        self.assertEqual(updated_state["score"], 100 + 300 + 500)
        self.assertEqual(updated_state["lines_cleared"], 6)
        
        # Очистка четырех линий (Tetris)
        updated_state = self.game_logic.update_score(updated_state, 4)
        self.assertEqual(updated_state["score"], 100 + 300 + 500 + 800)
        self.assertEqual(updated_state["lines_cleared"], 10)
    
    def test_06_game_over_detection(self):
        """Проверка обнаружения окончания игры"""
        # Создание тестового состояния игры с блоками в верхней части
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": [
                {"id": i, "x": i, "y": 0, "width": 1, "height": 1} for i in range(10)
            ]
        }
        
        # Проверка обнаружения окончания игры
        self.assertTrue(self.game_logic.check_game_over(game_state))
        
        # Создание тестового состояния игры с блоками только внизу
        game_state = {
            "board": [[0 for _ in range(10)] for _ in range(20)],
            "tower_blocks": [
                {"id": i, "x": i, "y": 19, "width": 1, "height": 1} for i in range(10)
            ]
        }
        
        # Проверка отсутствия окончания игры
        self.assertFalse(self.game_logic.check_game_over(game_state))


class TestCppPhysicsEngine(unittest.TestCase):
    """
    Тесты для проверки физического движка на C++
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        self.base_url = "http://localhost:9000"
        
        # Сброс физического мира
        try:
            requests.post(f"{self.base_url}/physics/reset")
        except:
            self.skipTest("Physics engine not available")
    
    def test_01_block_creation(self):
        """Проверка создания блока"""
        block_payload = {
            "x": 5.0,
            "y": 10.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        response = requests.post(f"{self.base_url}/physics/add_block", json=block_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("block_id", data)
        
        # Проверка, что блок добавлен
        response = requests.get(f"{self.base_url}/physics/blocks")
        self.assertEqual(response.status_code, 200)
        blocks = response.json()["blocks"]
        
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["id"], data["block_id"])
        self.assertEqual(blocks[0]["x"], 5.0)
        self.assertEqual(blocks[0]["y"], 10.0)
    
    def test_02_gravity_simulation(self):
        """Проверка симуляции гравитации"""
        # Создание блока
        block_payload = {
            "x": 5.0,
            "y": 10.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        response = requests.post(f"{self.base_url}/physics/add_block", json=block_payload)
        block_id = response.json()["block_id"]
        
        # Запуск симуляции на несколько шагов
        for _ in range(10):
            sim_payload = {
                "time_step": 0.016  # ~60 FPS
            }
            requests.post(f"{self.base_url}/physics/step", json=sim_payload)
        
        # Получение состояния блоков
        response = requests.get(f"{self.base_url}/physics/blocks")
        blocks = response.json()["blocks"]
        
        # Проверка, что блок упал (Y-координата увеличилась)
        block = next(b for b in blocks if b["id"] == block_id)
        self.assertGreater(block["y"], 10.0)
    
    def test_03_collision_response(self):
        """Проверка реакции на столкновения"""
        # Создание статического блока (пол)
        floor_payload = {
            "x": 5.0,
            "y": 19.0,
            "width": 10.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 0.0,
            "friction": 0.3,
            "restitution": 0.1,
            "is_static": True
        }
        
        requests.post(f"{self.base_url}/physics/add_block", json=floor_payload)
        
        # Создание динамического блока над полом
        block_payload = {
            "x": 5.0,
            "y": 15.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        response = requests.post(f"{self.base_url}/physics/add_block", json=block_payload)
        block_id = response.json()["block_id"]
        
        # Запуск симуляции на много шагов, чтобы блок упал на пол
        for _ in range(50):
            sim_payload = {
                "time_step": 0.016  # ~60 FPS
            }
            requests.post(f"{self.base_url}/physics/step", json=sim_payload)
        
        # Получение состояния блоков
        response = requests.get(f"{self.base_url}/physics/blocks")
        blocks = response.json()["blocks"]
        
        # Проверка, что блок остановился на полу
        block = next(b for b in blocks if b["id"] == block_id)
        self.assertLess(block["y"], 19.0)  # Блок должен быть над полом
        self.assertGreater(block["y"], 14.0)  # Но ниже начальной позиции
    
    def test_04_block_stacking(self):
        """Проверка укладки блоков друг на друга"""
        # Создание статического блока (пол)
        floor_payload = {
            "x": 5.0,
            "y": 19.0,
            "width": 10.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 0.0,
            "friction": 0.3,
            "restitution": 0.1,
            "is_static": True
        }
        
        requests.post(f"{self.base_url}/physics/add_block", json=floor_payload)
        
        # Создание первого блока
        block1_payload = {
            "x": 5.0,
            "y": 15.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        response = requests.post(f"{self.base_url}/physics/add_block", json=block1_payload)
        block1_id = response.json()["block_id"]
        
        # Создание второго блока над первым
        block2_payload = {
            "x": 5.0,
            "y": 13.0,
            "width": 1.0,
            "height": 1.0,
            "rotation": 0.0,
            "density": 1.0,
            "friction": 0.3,
            "restitution": 0.1
        }
        
        response = requests.post(f"{self.base_url}/physics/add_block", json=block2_payload)
        block2_id = response.json()["block_id"]
        
        # Запуск симуляции на много шагов
        for _ in range(50):
            sim_payload = {
                "time_step": 0.016  # ~60 FPS
            }
            requests.post(f"{self.base_url}/physics/step", json=sim_payload)
        
        # Получение состояния блоков
        response = requests.get(f"{self.base_url}/physics/blocks")
        blocks = response.json()["blocks"]
        
        # Получение позиций блоков
        block1 = next(b for b in blocks if b["id"] == block1_id)
        block2 = next(b for b in blocks if b["id"] == block2_id)
        
        # Проверка, что блоки уложены друг на друга
        self.assertLess(block1["y"], 19.0)  # Первый блок над полом
        self.assertLess(block2["y"], block1["y"])  # Второй блок над первым


if __name__ == "__main__":
    unittest.main()
