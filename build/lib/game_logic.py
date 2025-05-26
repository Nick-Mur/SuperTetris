import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import random
import uuid

class TetrominoType(Enum):
    I = 'I'
    J = 'J'
    L = 'L'
    O = 'O'
    S = 'S'
    T = 'T'
    Z = 'Z'

class GameMode(Enum):
    RACE = 'RACE'
    SURVIVAL = 'SURVIVAL'
    PUZZLE = 'PUZZLE'

class GameLogic:
    """
    Класс, реализующий основную логику игры Tetris с элементами Tricky Towers
    """
    
    def __init__(self):
        """Инициализация игровой логики"""
        # Конфигурация форм тетромино
        self.TETROMINO_SHAPES = {
            TetrominoType.I: [(0, 0), (1, 0), (2, 0), (3, 0)],
            TetrominoType.J: [(0, 0), (0, 1), (1, 1), (2, 1)],
            TetrominoType.L: [(2, 0), (0, 1), (1, 1), (2, 1)],
            TetrominoType.O: [(0, 0), (1, 0), (0, 1), (1, 1)],
            TetrominoType.S: [(1, 0), (2, 0), (0, 1), (1, 1)],
            TetrominoType.T: [(1, 0), (0, 1), (1, 1), (2, 1)],
            TetrominoType.Z: [(0, 0), (1, 0), (1, 1), (2, 1)]
        }
        
        # Конфигурация цветов для тетромино
        self.TETROMINO_COLORS = {
            TetrominoType.I: '#00FFFF',  # Cyan
            TetrominoType.J: '#0000FF',  # Blue
            TetrominoType.L: '#FF7F00',  # Orange
            TetrominoType.O: '#FFFF00',  # Yellow
            TetrominoType.S: '#00FF00',  # Green
            TetrominoType.T: '#800080',  # Purple
            TetrominoType.Z: '#FF0000'   # Red
        }
        
        # Очки за очистку линий
        self.LINE_CLEAR_SCORES = {
            1: 100,   # Одна линия
            2: 300,   # Две линии
            3: 500,   # Три линии
            4: 800    # Четыре линии (Tetris)
        }
    
    def generate_tetromino(self) -> Dict[str, Any]:
        """
        Генерация нового тетромино
        
        Returns:
            Dict[str, Any]: Словарь с информацией о тетромино
        """
        tetromino_type = random.choice(list(TetrominoType))
        
        # Начальная позиция тетромино (по центру верхней части поля)
        x = 3  # Центр поля (поле шириной 10)
        y = 0  # Верхняя часть поля
        
        return {
            "type": tetromino_type.value,  # Возвращаем строковое значение для совместимости с тестами
            "x": x,
            "y": y,
            "rotation": 0
        }
    
    def check_collision(self, game_state: Dict[str, Any], x: int, y: int, 
                        tetromino_type: TetrominoType, rotation: int) -> bool:
        """
        Проверка коллизии тетромино с границами поля или другими блоками
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            x (int): X-координата тетромино
            y (int): Y-координата тетромино
            tetromino_type (TetrominoType): Тип тетромино
            rotation (int): Угол поворота тетромино (0, 90, 180, 270)
            
        Returns:
            bool: True, если есть коллизия, False в противном случае
        """
        # Получение формы тетромино
        if isinstance(tetromino_type, str):
            tetromino_type = TetrominoType(tetromino_type)
            
        shape = self.TETROMINO_SHAPES[tetromino_type]
        
        # Применение поворота
        rotated_shape = self._rotate_shape(shape, rotation)
        
        # Проверка коллизии с границами поля
        for block_x, block_y in rotated_shape:
            # Абсолютные координаты блока
            abs_x = x + block_x
            abs_y = y + block_y
            
            # Проверка выхода за границы поля
            if abs_x < 0 or abs_x >= 10 or abs_y < 0 or abs_y >= 20:
                return True
            
            # Проверка коллизии с другими блоками
            for block in game_state["tower_blocks"]:
                if abs_x == block["x"] and abs_y == block["y"]:
                    return True
        
        return False
    
    def _rotate_shape(self, shape: List[Tuple[int, int]], rotation: int) -> List[Tuple[int, int]]:
        """
        Поворот формы тетромино
        
        Args:
            shape (List[Tuple[int, int]]): Исходная форма тетромино
            rotation (int): Угол поворота (0, 90, 180, 270)
            
        Returns:
            List[Tuple[int, int]]: Повернутая форма тетромино
        """
        # Нормализация угла поворота
        rotation = rotation % 360
        
        if rotation == 0:
            return shape
        
        rotated_shape = []
        
        for x, y in shape:
            if rotation == 90:
                rotated_shape.append((y, -x))
            elif rotation == 180:
                rotated_shape.append((-x, -y))
            elif rotation == 270:
                rotated_shape.append((-y, x))
        
        # Нормализация координат (смещение, чтобы все координаты были неотрицательными)
        min_x = min(x for x, _ in rotated_shape)
        min_y = min(y for _, y in rotated_shape)
        
        return [(x - min_x, y - min_y) for x, y in rotated_shape]
    
    def place_tetromino(self, game_state: Dict[str, Any], tetromino: Dict[str, Any]) -> Dict[str, Any]:
        """
        Размещение тетромино на игровом поле
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            tetromino (Dict[str, Any]): Информация о тетромино
            
        Returns:
            Dict[str, Any]: Обновленное состояние игры
        """
        # Создание копии состояния игры
        updated_state = {
            "board": game_state["board"].copy(),
            "tower_blocks": game_state["tower_blocks"].copy()
        }
        
        # Получение формы тетромино
        tetromino_type = tetromino["type"]
        if isinstance(tetromino_type, str):
            tetromino_type = TetrominoType(tetromino_type)
            
        shape = self.TETROMINO_SHAPES[tetromino_type]
        
        # Применение поворота
        rotated_shape = self._rotate_shape(shape, tetromino["rotation"])
        
        # Добавление блоков тетромино в башню
        for block_x, block_y in rotated_shape:
            # Абсолютные координаты блока
            abs_x = tetromino["x"] + block_x
            abs_y = tetromino["y"] + block_y
            
            # Создание нового блока
            block = {
                "id": len(updated_state["tower_blocks"]) + 1,
                "x": abs_x,
                "y": abs_y,
                "width": 1,
                "height": 1,
                "rotation": 0,
                "color": self.TETROMINO_COLORS[tetromino_type],
                "density": 1.0,
                "friction": 0.3,
                "restitution": 0.1,
                "isStatic": False
            }
            
            # Добавление блока в башню
            updated_state["tower_blocks"].append(block)
            
            # Обновление игрового поля
            updated_state["board"][abs_y][abs_x] = 1
        
        return updated_state
    
    def check_and_clear_lines(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверка и очистка заполненных линий
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            
        Returns:
            Dict[str, Any]: Обновленное состояние игры и количество очищенных линий
        """
        # Создание копии состояния игры
        updated_state = {
            "board": game_state["board"].copy(),
            "tower_blocks": game_state["tower_blocks"].copy()
        }
        
        # Создание сетки для проверки заполненных линий
        grid = [[0 for _ in range(10)] for _ in range(20)]
        
        # Заполнение сетки блоками
        for block in updated_state["tower_blocks"]:
            x, y = block["x"], block["y"]
            if 0 <= x < 10 and 0 <= y < 20:
                grid[y][x] = 1
        
        # Поиск заполненных линий
        full_lines = []
        for y in range(20):
            if all(grid[y]):
                full_lines.append(y)
        
        # Если нет заполненных линий, возвращаем исходное состояние
        if not full_lines:
            return updated_state
        
        # Удаление блоков из заполненных линий
        updated_state["tower_blocks"] = [
            block for block in updated_state["tower_blocks"]
            if block["y"] not in full_lines
        ]
        
        # Смещение блоков вниз
        for block in updated_state["tower_blocks"]:
            # Подсчет количества очищенных линий ниже текущего блока
            lines_below = sum(1 for line in full_lines if line > block["y"])
            # Смещение блока вниз
            block["y"] += lines_below
        
        # Обновление игрового поля
        updated_state["board"] = [[0 for _ in range(10)] for _ in range(20)]
        for block in updated_state["tower_blocks"]:
            x, y = block["x"], block["y"]
            if 0 <= x < 10 and 0 <= y < 20:
                updated_state["board"][y][x] = 1
        
        return updated_state
    
    def update_score(self, player_state: Dict[str, Any], lines_cleared: int) -> Dict[str, Any]:
        """
        Обновление счета игрока
        
        Args:
            player_state (Dict[str, Any]): Текущее состояние игрока
            lines_cleared (int): Количество очищенных линий
            
        Returns:
            Dict[str, Any]: Обновленное состояние игрока
        """
        # Создание копии состояния игрока
        updated_state = player_state.copy()
        
        # Обновление счета
        if lines_cleared in self.LINE_CLEAR_SCORES:
            updated_state["score"] += self.LINE_CLEAR_SCORES[lines_cleared]
        
        # Обновление количества очищенных линий
        updated_state["lines_cleared"] += lines_cleared
        
        return updated_state
    
    def check_game_over(self, game_state: Dict[str, Any]) -> bool:
        """
        Проверка окончания игры
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            
        Returns:
            bool: True, если игра окончена, False в противном случае
        """
        # Проверка наличия блоков в верхней части поля
        for block in game_state["tower_blocks"]:
            if block["y"] <= 1:  # Если есть блоки в первых двух рядах
                return True
        
        return False
    
    def apply_physics(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Применение физики к блокам
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            
        Returns:
            Dict[str, Any]: Обновленное состояние игры
        """
        # В реальной реализации здесь был бы вызов физического движка
        # Для тестов просто возвращаем исходное состояние
        return game_state
    
    def apply_spell(self, game_state: Dict[str, Any], spell_type: str, 
                   caster_id: int, target_id: int) -> Dict[str, Any]:
        """
        Применение заклинания
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            spell_type (str): Тип заклинания
            caster_id (int): ID игрока, применяющего заклинание
            target_id (int): ID целевого игрока
            
        Returns:
            Dict[str, Any]: Обновленное состояние игры
        """
        # В реальной реализации здесь была бы логика применения заклинаний
        # Для тестов просто возвращаем исходное состояние
        return game_state
    
    def generate_ai_move(self, game_state: Dict[str, Any], player_id: int) -> Dict[str, Any]:
        """
        Генерация хода ИИ
        
        Args:
            game_state (Dict[str, Any]): Текущее состояние игры
            player_id (int): ID игрока ИИ
            
        Returns:
            Dict[str, Any]: Информация о ходе ИИ
        """
        # В реальной реализации здесь был бы вызов системы ИИ
        # Для тестов просто возвращаем случайный ход
        return {
            "action_type": "move",
            "x": random.randint(0, 9),
            "y": random.randint(0, 19),
            "rotation": random.choice([0, 90, 180, 270])
        }
    
    def create_new_game(self, mode: GameMode, player_names: List[str], 
                       difficulty: str = "medium") -> Dict[str, Any]:
        """
        Создание новой игры
        
        Args:
            mode (GameMode): Режим игры
            player_names (List[str]): Имена игроков
            difficulty (str, optional): Сложность игры. По умолчанию "medium".
            
        Returns:
            Dict[str, Any]: Начальное состояние игры
        """
        # Создание игроков
        players = {}
        for i, name in enumerate(player_names):
            players[str(i + 1)] = {
                "id": i + 1,
                "name": name,
                "towerBlocks": [],
                "currentTetromino": self.generate_tetromino(),
                "nextTetrominos": [self.generate_tetromino() for _ in range(3)],
                "heldTetromino": None,
                "spells": [],
                "score": 0,
                "health": 3,
                "lines_cleared": 0
            }
        
        # Создание игрового состояния
        game_state = {
            "players": players,
            "gameMode": mode,
            "currentTurn": 1,
            "gameStatus": "PLAYING",
            "timer": 0,
            "difficulty": difficulty,
            "session_id": str(uuid.uuid4())
        }
        
        return game_state
