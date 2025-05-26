from datetime import datetime
from typing import Dict, List, Union
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

from ..models.data_models import GameEvent, GameplayMetrics, AnalyticsResults

class GameplayAnalyzer:
    """Анализатор данных о геймплее"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, events: List[GameEvent], metrics: List[GameplayMetrics]) -> Dict[str, Union[float, int, List[float]]]:
        """Проанализировать данные о геймплее"""
        try:
            # Конвертируем в DataFrame
            events_df = pd.DataFrame([{
                'event_id': str(e.event_id),
                'game_id': str(e.game_id),
                'player_id': str(e.player_id),
                'event_type': e.event_type,
                'timestamp': e.timestamp,
                **e.data
            } for e in events])
            
            metrics_df = pd.DataFrame([{
                'game_id': str(m.game_id),
                'player_id': str(m.player_id),
                'score': m.score,
                'lines_cleared': m.lines_cleared,
                'time_played': m.time_played,
                'pieces_placed': m.pieces_placed,
                'level': m.level,
                'timestamp': m.timestamp
            } for m in metrics])
            
            # Базовые метрики
            results = {
                'total_games': len(metrics_df['game_id'].unique()),
                'total_players': len(metrics_df['player_id'].unique()),
                'average_score': metrics_df['score'].mean(),
                'average_lines_cleared': metrics_df['lines_cleared'].mean(),
                'average_time_played': metrics_df['time_played'].mean(),
                'average_pieces_placed': metrics_df['pieces_placed'].mean(),
                'average_level': metrics_df['level'].mean(),
            }
            
            # Анализ событий
            event_counts = events_df['event_type'].value_counts()
            results['event_distribution'] = event_counts.to_dict()
            
            # Анализ производительности игроков
            player_metrics = metrics_df.groupby('player_id').agg({
                'score': ['mean', 'max', 'sum'],
                'lines_cleared': ['mean', 'max', 'sum'],
                'time_played': ['mean', 'max', 'sum'],
                'pieces_placed': ['mean', 'max', 'sum'],
                'level': ['mean', 'max']
            })
            
            results['player_performance'] = {
                'average_score_per_player': player_metrics[('score', 'mean')].mean(),
                'max_score': player_metrics[('score', 'max')].max(),
                'average_lines_per_player': player_metrics[('lines_cleared', 'mean')].mean(),
                'max_lines': player_metrics[('lines_cleared', 'max')].max(),
                'average_time_per_player': player_metrics[('time_played', 'mean')].mean(),
                'max_time': player_metrics[('time_played', 'max')].max(),
            }
            
            # Кластеризация игроков
            if len(metrics_df) >= 3:  # Минимум 3 игрока для кластеризации
                features = ['score', 'lines_cleared', 'time_played', 'pieces_placed', 'level']
                X = metrics_df[features].values
                
                # Нормализация данных
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Кластеризация
                kmeans = KMeans(n_clusters=min(3, len(metrics_df)), random_state=42)
                clusters = kmeans.fit_predict(X_scaled)
                
                # Анализ кластеров
                metrics_df['cluster'] = clusters
                cluster_analysis = metrics_df.groupby('cluster')[features].mean()
                
                results['player_clusters'] = {
                    'cluster_centers': cluster_analysis.to_dict(),
                    'cluster_sizes': metrics_df['cluster'].value_counts().to_dict()
                }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing gameplay data: {e}")
            return {} 