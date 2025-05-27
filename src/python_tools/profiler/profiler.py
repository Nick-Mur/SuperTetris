"""
Performance Profiler Implementation
"""

import cProfile
import pstats
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Callable
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class PerformanceProfiler:
    def __init__(self):
        self.console = Console()
        self.profiles_dir = Path("data/profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main profiler loop"""
        while True:
            self.console.print("\n[bold blue]Tetris Performance Profiler[/bold blue]")
            self.console.print("1. Profile function")
            self.console.print("2. Profile game session")
            self.console.print("3. Generate performance report")
            self.console.print("4. Exit")

            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])

            if choice == "1":
                self.profile_function()
            elif choice == "2":
                self.profile_session()
            elif choice == "3":
                self.generate_report()
            elif choice == "4":
                break

    def profile_function(self):
        """Profile a specific function"""
        module_name = Prompt.ask("Enter module name")
        function_name = Prompt.ask("Enter function name")
        
        try:
            # Динамический импорт модуля
            module = __import__(module_name, fromlist=[function_name])
            function = getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return

        # Профилирование функции
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            function()
        except Exception as e:
            self.console.print(f"[red]Error executing function: {str(e)}[/red]")
            return
        finally:
            profiler.disable()

        # Сохранение результатов
        stats = pstats.Stats(profiler)
        output_file = self.profiles_dir / f"profile_{module_name}_{function_name}.prof"
        stats.dump_stats(str(output_file))
        
        # Вывод основных метрик
        table = Table(title="Function Profile Results")
        table.add_column("Metric")
        table.add_column("Value")
        
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        
        # Получение топ-10 самых затратных вызовов
        top_calls = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            if isinstance(func, tuple):
                name = f"{func[0]}:{func[1]}:{func[2]}"
            else:
                name = str(func)
            top_calls.append((name, ct))
        
        top_calls.sort(key=lambda x: x[1], reverse=True)
        
        for name, time in top_calls[:10]:
            table.add_row(name, f"{time:.4f}s")
        
        self.console.print(table)
        self.console.print(f"[green]Profile saved to {output_file}[/green]")

    def profile_session(self):
        """Profile a game session"""
        session_file = Prompt.ask("Enter session file path")
        try:
            with open(session_file) as f:
                session_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.console.print(f"[red]Error loading session: {str(e)}[/red]")
            return

        # Профилирование сессии
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            # Здесь должна быть логика выполнения сессии
            # Для примера просто эмулируем работу
            time.sleep(1)
        except Exception as e:
            self.console.print(f"[red]Error profiling session: {str(e)}[/red]")
            return
        finally:
            profiler.disable()

        # Сохранение результатов
        stats = pstats.Stats(profiler)
        output_file = self.profiles_dir / f"profile_session_{session_data['session_id']}.prof"
        stats.dump_stats(str(output_file))
        
        self.console.print(f"[green]Session profile saved to {output_file}[/green]")

    def generate_report(self):
        """Generate performance report"""
        # Получение всех файлов профилирования
        profile_files = list(self.profiles_dir.glob("profile_*.prof"))
        if not profile_files:
            self.console.print("[yellow]No profile data found![/yellow]")
            return

        # Анализ профилей
        results = []
        for file in profile_files:
            stats = pstats.Stats(str(file))
            stats.strip_dirs()
            stats.sort_stats('cumulative')
            
            # Сбор основных метрик
            total_time = sum(stat[3] for stat in stats.stats.values())
            call_count = sum(stat[1] for stat in stats.stats.values())
            
            results.append({
                "file": file.name,
                "total_time": total_time,
                "call_count": call_count
            })

        # Создание графика
        plt.figure(figsize=(10, 6))
        
        # График времени выполнения
        plt.subplot(1, 2, 1)
        sns.barplot(data=pd.DataFrame(results), x="file", y="total_time")
        plt.title("Execution Time by Profile")
        plt.xticks(rotation=45)
        
        # График количества вызовов
        plt.subplot(1, 2, 2)
        sns.barplot(data=pd.DataFrame(results), x="file", y="call_count")
        plt.title("Call Count by Profile")
        plt.xticks(rotation=45)
        
        # Сохранение отчета
        report_file = self.reports_dir / "performance_profile_report.png"
        plt.tight_layout()
        plt.savefig(report_file)
        plt.close()
        
        self.console.print(f"[green]Report generated: {report_file}[/green]") 