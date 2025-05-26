from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AnalyticsConfig:
    """Конфигурация аналитической системы"""
    
    # Настройки базы данных
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "tetris_analytics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    
    # Настройки API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8082"))
    
    # Настройки логирования
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "analytics.log")
    
    # Настройки анализа
    analysis_interval: int = int(os.getenv("ANALYSIS_INTERVAL", "3600"))  # в секундах
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))
    
    # Настройки алертов
    alert_threshold_score: float = float(os.getenv("ALERT_THRESHOLD_SCORE", "0.8"))
    alert_threshold_performance: float = float(os.getenv("ALERT_THRESHOLD_PERFORMANCE", "0.9"))
    
    # Настройки отчетов
    report_output_dir: str = os.getenv("REPORT_OUTPUT_DIR", "reports")
    report_format: str = os.getenv("REPORT_FORMAT", "html")
    
    def get_database_url(self) -> str:
        """Получить URL для подключения к базе данных"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def get_api_url(self) -> str:
        """Получить URL для API"""
        return f"http://{self.api_host}:{self.api_port}" 