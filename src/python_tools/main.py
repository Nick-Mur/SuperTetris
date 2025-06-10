"""
Main module for Python Development Tools
"""

import click
from rich.console import Console
from rich.logging import RichHandler
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("python_tools")
console = Console()

# FastAPI приложение
app = FastAPI(title="Tetris Development Tools")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Эндпоинты для совместимости с существующим API
@app.get("/api/v1/dev/status")
async def get_status():
    return {"status": "running", "version": "1.0.0"}

# CLI интерфейс
@click.group()
def cli():
    """Tetris Development Tools"""
    pass

@cli.command()
def editor():
    """Level editor"""
    from .editor import LevelEditor
    editor = LevelEditor()
    editor.run()

@cli.command()
def generator():
    """Level generator"""
    from .generator import LevelGenerator
    generator = LevelGenerator()
    generator.run()

@cli.command()
def analyzer():
    """Game data analyzer"""
    from .analyzer import GameAnalyzer
    analyzer = GameAnalyzer()
    analyzer.run()

@cli.command()
def profiler():
    """Performance profiler"""
    from .profiler import PerformanceProfiler
    profiler = PerformanceProfiler()
    profiler.run()

def start_server():
    """Start FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    print("python_tools main entry. Add your tool logic here.")

    cli() 