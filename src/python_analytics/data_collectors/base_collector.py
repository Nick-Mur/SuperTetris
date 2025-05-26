from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import AnalyticsConfig
from ..models.data_models import GameEvent, PlayerAction, PerformanceMetrics

T = TypeVar('T')

class BaseCollector(Generic[T], ABC):
    """Базовый класс для сборщиков данных"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.engine = create_engine(config.get_database_url())
        self.Session = sessionmaker(bind=self.engine)
        self._running = False
        
    def start(self):
        """Запустить сборщик"""
        self._running = True
        self.logger.info(f"Starting {self.__class__.__name__}")
        
    def stop(self):
        """Остановить сборщик"""
        self._running = False
        self.logger.info(f"Stopping {self.__class__.__name__}")
        
    @abstractmethod
    def collect(self, data: T) -> None:
        """Собрать данные"""
        pass
    
    @abstractmethod
    def get_data(self, start_time: datetime = None, end_time: datetime = None) -> List[T]:
        """Получить собранные данные за период"""
        pass
    
    def cleanup_old_data(self):
        """Очистить старые данные"""
        retention_date = datetime.now() - timedelta(days=self.config.data_retention_days)
        self.logger.info(f"Cleaning up data older than {retention_date}")
        # Реализация очистки в подклассах 