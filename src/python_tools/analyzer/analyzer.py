"""
Game Data Analyzer Implementation
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress
import matplotlib.pyplot as plt
import seaborn as sns

class GameAnalyzer:
    def __init__(self):
        self.console = Console()
        self.data_dir = Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main analyzer loop"""
        while True:
            self.console.print("\n[bold blue]Tetris Game Data Analyzer[/bold blue]")
            self.console.print("1. Analyze game session")
            self.console.print("2. Generate performance report")
            self.console.print("3. Compare sessions")
            self.console.print("4. Exit")

            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])

            if choice == "1":
                self.analyze_session()
            elif choice == "2":
                self.generate_report()
            elif choice == "3":
                self.compare_sessions()
            elif choice == "4":
                break

    def analyze_session(self):
        """Analyze a single game session"""
        session_file = Prompt.ask("Enter session file path")
        try:
            with open(session_file) as f:
                session_data = json.load(f)
        except FileNotFoundError:
            self.console.print("[red]Session file not found![/red]")
            return
        except json.JSONDecodeError:
            self.console.print("[red]Invalid session file format![/red]")
            return

        # Анализ данных
        df = pd.DataFrame(session_data['events'])
        
        # Базовые метрики
        total_score = df['score'].sum()
        max_combo = df['combo'].max()
        avg_speed = df['speed'].mean()
        
        # Создание таблицы с результатами
        table = Table(title="Session Analysis Results")
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Total Score", str(total_score))
        table.add_row("Max Combo", str(max_combo))
        table.add_row("Average Speed", f"{avg_speed:.2f}")
        
        self.console.print(table)
        
        # Сохранение результатов
        results = {
            "session_id": session_data['session_id'],
            "total_score": total_score,
            "max_combo": max_combo,
            "avg_speed": avg_speed,
            "timestamp": session_data['timestamp']
        }
        
        output_file = self.data_dir / f"analysis_{session_data['session_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.console.print(f"[green]Analysis saved to {output_file}[/green]")

    def generate_report(self):
        """Generate performance report"""
        # Получение всех файлов анализа
        analysis_files = list(self.data_dir.glob("analysis_*.json"))
        if not analysis_files:
            self.console.print("[yellow]No analysis data found![/yellow]")
            return

        # Загрузка и объединение данных
        all_data = []
        for file in analysis_files:
            with open(file) as f:
                all_data.append(json.load(f))
        
        df = pd.DataFrame(all_data)
        
        # Генерация графиков
        plt.figure(figsize=(15, 10))
        
        # График распределения очков
        plt.subplot(2, 2, 1)
        sns.histplot(data=df, x="total_score", bins=20)
        plt.title("Score Distribution")
        
        # График зависимости скорости от комбо
        plt.subplot(2, 2, 2)
        sns.scatterplot(data=df, x="max_combo", y="avg_speed")
        plt.title("Speed vs Combo")
        
        # График тренда очков
        plt.subplot(2, 2, 3)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
        plt.plot(df['timestamp'], df['total_score'])
        plt.title("Score Trend")
        plt.xticks(rotation=45)
        
        # Сохранение отчета
        report_file = self.reports_dir / "performance_report.png"
        plt.tight_layout()
        plt.savefig(report_file)
        plt.close()
        
        self.console.print(f"[green]Report generated: {report_file}[/green]")

    def compare_sessions(self):
        """Compare multiple sessions"""
        # Получение списка сессий для сравнения
        session_files = Prompt.ask("Enter session file paths (comma-separated)").split(',')
        
        if len(session_files) < 2:
            self.console.print("[yellow]Need at least 2 sessions to compare![/yellow]")
            return
        
        # Загрузка данных
        sessions_data = []
        for file in session_files:
            try:
                with open(file.strip()) as f:
                    sessions_data.append(json.load(f))
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.console.print(f"[red]Error loading {file}: {str(e)}[/red]")
                return
        
        # Создание таблицы сравнения
        table = Table(title="Session Comparison")
        table.add_column("Session ID")
        table.add_column("Total Score")
        table.add_column("Max Combo")
        table.add_column("Avg Speed")
        
        for session in sessions_data:
            df = pd.DataFrame(session['events'])
            table.add_row(
                session['session_id'],
                str(df['score'].sum()),
                str(df['combo'].max()),
                f"{df['speed'].mean():.2f}"
            )
        
        self.console.print(table) 