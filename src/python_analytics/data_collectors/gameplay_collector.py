from datetime import datetime, timedelta
from typing import List
import logging
from sqlalchemy import select, and_

from .base_collector import BaseCollector
from ..models.data_models import GameEvent, GameplayMetrics
from ..config import AnalyticsConfig

class GameplayCollector(BaseCollector[GameEvent]):
    """Сборщик данных о геймплее"""
    
    def __init__(self, config: AnalyticsConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    def collect(self, event: GameEvent) -> None:
        """Собрать данные о событии в игре"""
        if not self._running:
            self.logger.warning("Collector is not running")
            return
            
        try:
            with self.Session() as session:
                # Сохраняем событие
                session.add(event)
                session.commit()
                self.logger.debug(f"Collected game event: {event.event_id}")
        except Exception as e:
            self.logger.error(f"Error collecting game event: {e}")
            session.rollback()
            
    def get_data(self, start_time: datetime = None, end_time: datetime = None) -> List[GameEvent]:
        """Получить события за период"""
        try:
            with self.Session() as session:
                query = select(GameEvent)
                
                if start_time:
                    query = query.where(GameEvent.timestamp >= start_time)
                if end_time:
                    query = query.where(GameEvent.timestamp <= end_time)
                    
                events = session.execute(query).scalars().all()
                return list(events)
        except Exception as e:
            self.logger.error(f"Error getting game events: {e}")
            return []
            
    def get_gameplay_metrics(self, game_id: str) -> List[GameplayMetrics]:
        """Получить метрики геймплея для конкретной игры"""
        try:
            with self.Session() as session:
                query = select(GameplayMetrics).where(GameplayMetrics.game_id == game_id)
                metrics = session.execute(query).scalars().all()
                return list(metrics)
        except Exception as e:
            self.logger.error(f"Error getting gameplay metrics: {e}")
            return []
            
    def cleanup_old_data(self):
        """Очистить старые данные"""
        retention_date = datetime.now() - timedelta(days=self.config.data_retention_days)
        try:
            with self.Session() as session:
                # Удаляем старые события
                session.query(GameEvent).filter(
                    GameEvent.timestamp < retention_date
                ).delete()
                
                # Удаляем старые метрики
                session.query(GameplayMetrics).filter(
                    GameplayMetrics.timestamp < retention_date
                ).delete()
                
                session.commit()
                self.logger.info(f"Cleaned up data older than {retention_date}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
            session.rollback() 