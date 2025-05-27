"""
Data Validation Utilities
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path

def validate_level_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate level data structure
    
    Args:
        data: Level data dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Проверка обязательных полей
    required_fields = ["name", "difficulty", "grid_size", "blocks", "spawn_points"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Проверка типа сложности
    valid_difficulties = ["easy", "medium", "hard"]
    if data["difficulty"] not in valid_difficulties:
        errors.append(f"Invalid difficulty: {data['difficulty']}")
    
    # Проверка размеров сетки
    if not isinstance(data["grid_size"], dict):
        errors.append("grid_size must be a dictionary")
    else:
        if "width" not in data["grid_size"] or "height" not in data["grid_size"]:
            errors.append("grid_size must contain width and height")
        else:
            if not isinstance(data["grid_size"]["width"], int) or data["grid_size"]["width"] <= 0:
                errors.append("grid_size.width must be a positive integer")
            if not isinstance(data["grid_size"]["height"], int) or data["grid_size"]["height"] <= 0:
                errors.append("grid_size.height must be a positive integer")
    
    # Проверка блоков
    if not isinstance(data["blocks"], list):
        errors.append("blocks must be a list")
    else:
        valid_block_types = ["I", "J", "L", "O", "S", "T", "Z"]
        for i, block in enumerate(data["blocks"]):
            if not isinstance(block, dict):
                errors.append(f"Block {i} must be a dictionary")
                continue
            
            if "type" not in block or block["type"] not in valid_block_types:
                errors.append(f"Block {i} has invalid type")
            
            if "x" not in block or not isinstance(block["x"], int):
                errors.append(f"Block {i} has invalid x coordinate")
            elif block["x"] < 0 or block["x"] >= data["grid_size"]["width"]:
                errors.append(f"Block {i} x coordinate out of bounds")
            
            if "y" not in block or not isinstance(block["y"], int):
                errors.append(f"Block {i} has invalid y coordinate")
            elif block["y"] < 0 or block["y"] >= data["grid_size"]["height"]:
                errors.append(f"Block {i} y coordinate out of bounds")
    
    # Проверка точек появления
    if not isinstance(data["spawn_points"], list):
        errors.append("spawn_points must be a list")
    else:
        for i, point in enumerate(data["spawn_points"]):
            if not isinstance(point, dict):
                errors.append(f"Spawn point {i} must be a dictionary")
                continue
            
            if "x" not in point or not isinstance(point["x"], int):
                errors.append(f"Spawn point {i} has invalid x coordinate")
            elif point["x"] < 0 or point["x"] >= data["grid_size"]["width"]:
                errors.append(f"Spawn point {i} x coordinate out of bounds")
            
            if "y" not in point or not isinstance(point["y"], int):
                errors.append(f"Spawn point {i} has invalid y coordinate")
            elif point["y"] != 0:
                errors.append(f"Spawn point {i} must be at y=0")
    
    return len(errors) == 0, errors

def validate_session_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate game session data structure
    
    Args:
        data: Session data dictionary
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Проверка обязательных полей
    required_fields = ["session_id", "timestamp", "events"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Проверка событий
    if not isinstance(data["events"], list):
        errors.append("events must be a list")
    else:
        for i, event in enumerate(data["events"]):
            if not isinstance(event, dict):
                errors.append(f"Event {i} must be a dictionary")
                continue
            
            if "type" not in event:
                errors.append(f"Event {i} missing type")
            
            if "timestamp" not in event:
                errors.append(f"Event {i} missing timestamp")
            
            if "score" in event and not isinstance(event["score"], (int, float)):
                errors.append(f"Event {i} score must be a number")
            
            if "combo" in event and not isinstance(event["combo"], int):
                errors.append(f"Event {i} combo must be an integer")
            
            if "speed" in event and not isinstance(event["speed"], (int, float)):
                errors.append(f"Event {i} speed must be a number")
    
    return len(errors) == 0, errors 