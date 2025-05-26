from datetime import datetime
import logging
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import AnalyticsConfig
from .models.data_models import AnalyticsResults

class AlertSystem:
    """Система алертов для аналитики"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._running = False
        
    def start(self):
        """Запустить систему алертов"""
        self._running = True
        self.logger.info("Starting alert system")
        
    def stop(self):
        """Остановить систему алертов"""
        self._running = False
        self.logger.info("Stopping alert system")
        
    def check_alerts(self, results: AnalyticsResults) -> List[Dict[str, Any]]:
        """Проверить условия для алертов"""
        if not self._running:
            return []
            
        alerts = []
        
        try:
            # Проверка метрик геймплея
            gameplay_results = results.gameplay_results
            
            # Проверка среднего счета
            if gameplay_results.get('average_score', 0) > self.config.alert_threshold_score:
                alerts.append({
                    'type': 'high_score',
                    'message': f'Средний счет превысил порог: {gameplay_results["average_score"]:.2f}',
                    'severity': 'warning',
                    'timestamp': datetime.now()
                })
                
            # Проверка производительности
            if gameplay_results.get('player_performance', {}).get('average_score_per_player', 0) > self.config.alert_threshold_performance:
                alerts.append({
                    'type': 'high_performance',
                    'message': f'Высокая производительность игроков: {gameplay_results["player_performance"]["average_score_per_player"]:.2f}',
                    'severity': 'info',
                    'timestamp': datetime.now()
                })
                
            # Проверка количества игр
            if gameplay_results.get('total_games', 0) > 1000:
                alerts.append({
                    'type': 'high_activity',
                    'message': f'Высокая активность: {gameplay_results["total_games"]} игр',
                    'severity': 'info',
                    'timestamp': datetime.now()
                })
                
            # Отправка алертов
            if alerts:
                self._send_alerts(alerts)
                
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
            return []
            
    def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Отправить алерты"""
        try:
            # Здесь можно добавить отправку через email, Slack, Telegram и т.д.
            for alert in alerts:
                self.logger.warning(f"Alert: {alert['message']}")
                
        except Exception as e:
            self.logger.error(f"Error sending alerts: {e}") 