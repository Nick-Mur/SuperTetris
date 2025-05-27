"""
Level Generator Implementation
"""

import random
import json
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress

class LevelGenerator:
    def __init__(self):
        self.console = Console()
        self.levels_dir = Path("data/levels")
        self.levels_dir.mkdir(parents=True, exist_ok=True)
        self.block_types = ["I", "J", "L", "O", "S", "T", "Z"]

    def run(self):
        """Main generator loop"""
        while True:
            self.console.print("\n[bold blue]Tetris Level Generator[/bold blue]")
            self.console.print("1. Generate single level")
            self.console.print("2. Generate level pack")
            self.console.print("3. Exit")

            choice = Prompt.ask("Select an option", choices=["1", "2", "3"])

            if choice == "1":
                self.generate_single_level()
            elif choice == "2":
                self.generate_level_pack()
            elif choice == "3":
                break

    def generate_single_level(self):
        """Generate a single level"""
        name = Prompt.ask("Level name")
        difficulty = Prompt.ask("Difficulty", choices=["easy", "medium", "hard"])
        width = int(Prompt.ask("Grid width", default="10"))
        height = int(Prompt.ask("Grid height", default="20"))
        
        level = self._generate_level(name, difficulty, width, height)
        self._save_level(level)

    def generate_level_pack(self):
        """Generate a pack of levels"""
        pack_name = Prompt.ask("Pack name")
        count = int(Prompt.ask("Number of levels", default="5"))
        difficulty = Prompt.ask("Base difficulty", choices=["easy", "medium", "hard"])
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating levels...", total=count)
            
            for i in range(count):
                level_name = f"{pack_name}_level_{i+1}"
                level = self._generate_level(level_name, difficulty, 10, 20)
                self._save_level(level)
                progress.update(task, advance=1)

    def _generate_level(self, name: str, difficulty: str, width: int, height: int) -> Dict[str, Any]:
        """Generate level data"""
        # Настройка параметров в зависимости от сложности
        difficulty_params = {
            "easy": {"min_blocks": 3, "max_blocks": 5, "special_rules": False},
            "medium": {"min_blocks": 5, "max_blocks": 8, "special_rules": True},
            "hard": {"min_blocks": 8, "max_blocks": 12, "special_rules": True}
        }
        
        params = difficulty_params[difficulty]
        
        # Генерация блоков
        blocks = []
        num_blocks = random.randint(params["min_blocks"], params["max_blocks"])
        
        for _ in range(num_blocks):
            block = {
                "type": random.choice(self.block_types),
                "x": random.randint(0, width - 1),
                "y": random.randint(0, height - 1)
            }
            blocks.append(block)
        
        # Генерация точек появления
        spawn_points = []
        for _ in range(3):
            spawn_points.append({
                "x": random.randint(0, width - 1),
                "y": 0
            })
        
        # Генерация специальных правил
        special_rules = {}
        if params["special_rules"]:
            if random.random() < 0.5:
                special_rules["gravity"] = random.uniform(0.5, 2.0)
            if random.random() < 0.3:
                special_rules["rotation_speed"] = random.uniform(0.5, 1.5)
        
        return {
            "name": name,
            "difficulty": difficulty,
            "grid_size": {
                "width": width,
                "height": height
            },
            "blocks": blocks,
            "spawn_points": spawn_points,
            "special_rules": special_rules
        }

    def _save_level(self, level: Dict[str, Any]) -> None:
        """Save generated level"""
        filename = f"{level['name'].lower().replace(' ', '_')}.json"
        filepath = self.levels_dir / filename
        
        if filepath.exists() and not Confirm.ask(f"File {filename} already exists. Overwrite?"):
            return
        
        with open(filepath, 'w') as f:
            json.dump(level, f, indent=2)
        self.console.print(f"[green]Level {level['name']} saved successfully![/green]") 