from datetime import datetime
import os
import json
import logging
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

from ..models.data_models import AnalyticsResults
from ..config import AnalyticsConfig

class DashboardReporter:
    """Генератор отчетов для дашборда"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.env = Environment(loader=FileSystemLoader('templates'))
        
        # Создаем директорию для отчетов, если её нет
        os.makedirs(config.report_output_dir, exist_ok=True)
        
    def generate_report(self, results: AnalyticsResults) -> str:
        """Сгенерировать отчет"""
        try:
            # Генерируем графики
            self._generate_charts(results)
            
            # Генерируем HTML отчет
            template = self.env.get_template('dashboard.html')
            report_html = template.render(
                results=results,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                charts=self._get_chart_paths()
            )
            
            # Сохраняем отчет
            report_path = os.path.join(
                self.config.report_output_dir,
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
                
            self.logger.info(f"Generated report: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return ""
            
    def _generate_charts(self, results: AnalyticsResults):
        """Сгенерировать графики"""
        try:
            # Настройка стиля
            plt.style.use('seaborn')
            sns.set_palette("husl")
            
            # График распределения событий
            if 'event_distribution' in results.gameplay_results:
                plt.figure(figsize=(10, 6))
                events = results.gameplay_results['event_distribution']
                plt.bar(events.keys(), events.values())
                plt.title('Распределение событий')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(os.path.join(self.config.report_output_dir, 'event_distribution.png'))
                plt.close()
            
            # График производительности игроков
            if 'player_performance' in results.gameplay_results:
                plt.figure(figsize=(12, 6))
                perf = results.gameplay_results['player_performance']
                metrics = ['average_score_per_player', 'average_lines_per_player', 'average_time_per_player']
                values = [perf[m] for m in metrics]
                plt.bar(metrics, values)
                plt.title('Средняя производительность игроков')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(os.path.join(self.config.report_output_dir, 'player_performance.png'))
                plt.close()
            
            # График кластеров игроков
            if 'player_clusters' in results.gameplay_results:
                clusters = results.gameplay_results['player_clusters']
                plt.figure(figsize=(10, 6))
                plt.pie(
                    clusters['cluster_sizes'].values(),
                    labels=[f'Кластер {i}' for i in clusters['cluster_sizes'].keys()],
                    autopct='%1.1f%%'
                )
                plt.title('Распределение игроков по кластерам')
                plt.tight_layout()
                plt.savefig(os.path.join(self.config.report_output_dir, 'player_clusters.png'))
                plt.close()
                
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            
    def _get_chart_paths(self) -> Dict[str, str]:
        """Получить пути к сгенерированным графикам"""
        return {
            'event_distribution': 'event_distribution.png',
            'player_performance': 'player_performance.png',
            'player_clusters': 'player_clusters.png'
        } 