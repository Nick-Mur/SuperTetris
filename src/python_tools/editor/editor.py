"""
Level Editor Implementation
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

class LevelEditor:
    def __init__(self):
        self.console = Console()
        self.current_level: Optional[Dict[str, Any]] = None
        self.levels_dir = Path("data/levels")
        self.levels_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main editor loop"""
        while True:
            self.console.print("\n[bold blue]Tetris Level Editor[/bold blue]")
            self.console.print("1. Create new level")
            self.console.print("2. Load existing level")
            self.console.print("3. Save current level")
            self.console.print("4. Edit level properties")
            self.console.print("5. Exit")

            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                self.create_new_level()
            elif choice == "2":
                self.load_level()
            elif choice == "3":
                self.save_level()
            elif choice == "4":
                self.edit_level()
            elif choice == "5":
                if self.current_level and not self.save_level():
                    if not Confirm.ask("Unsaved changes. Exit anyway?"):
                        continue
                break

    def create_new_level(self):
        """Create a new level"""
        self.current_level = {
            "name": Prompt.ask("Level name"),
            "difficulty": Prompt.ask("Difficulty", choices=["easy", "medium", "hard"]),
            "grid_size": {
                "width": int(Prompt.ask("Grid width", default="10")),
                "height": int(Prompt.ask("Grid height", default="20"))
            },
            "blocks": [],
            "spawn_points": [],
            "special_rules": {}
        }
        self.console.print("[green]New level created![/green]")

    def load_level(self):
        """Load an existing level"""
        levels = list(self.levels_dir.glob("*.json"))
        if not levels:
            self.console.print("[yellow]No levels found![/yellow]")
            return

        table = Table(title="Available Levels")
        table.add_column("Index")
        table.add_column("Name")
        table.add_column("Difficulty")

        for i, level_file in enumerate(levels, 1):
            with open(level_file) as f:
                level_data = json.load(f)
                table.add_row(str(i), level_data["name"], level_data["difficulty"])

        self.console.print(table)
        choice = int(Prompt.ask("Select level to load", choices=[str(i) for i in range(1, len(levels) + 1)]))
        
        with open(levels[choice - 1]) as f:
            self.current_level = json.load(f)
        self.console.print("[green]Level loaded successfully![/green]")

    def save_level(self) -> bool:
        """Save current level"""
        if not self.current_level:
            self.console.print("[yellow]No level to save![/yellow]")
            return False

        filename = f"{self.current_level['name'].lower().replace(' ', '_')}.json"
        filepath = self.levels_dir / filename

        if filepath.exists() and not Confirm.ask(f"File {filename} already exists. Overwrite?"):
            return False

        with open(filepath, 'w') as f:
            json.dump(self.current_level, f, indent=2)
        self.console.print("[green]Level saved successfully![/green]")
        return True

    def edit_level(self):
        """Edit level properties"""
        if not self.current_level:
            self.console.print("[yellow]No level loaded![/yellow]")
            return

        self.console.print("\n[bold]Current Level Properties:[/bold]")
        for key, value in self.current_level.items():
            if isinstance(value, dict):
                self.console.print(f"{key}:")
                for k, v in value.items():
                    self.console.print(f"  {k}: {v}")
            else:
                self.console.print(f"{key}: {value}")

        # Здесь можно добавить более сложную логику редактирования
        self.console.print("\n[bold]Edit Properties:[/bold]")
        self.current_level["name"] = Prompt.ask("Level name", default=self.current_level["name"])
        self.current_level["difficulty"] = Prompt.ask(
            "Difficulty",
            choices=["easy", "medium", "hard"],
            default=self.current_level["difficulty"]
        ) 