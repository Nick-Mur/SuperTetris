import os
import json
import csv
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

from .models.data_models import GameEvent, PlayerAction, PerformanceMetrics

class DataExporter:
    """Экспортер данных аналитики"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Создаем директорию для экспорта, если её нет
        os.makedirs(output_dir, exist_ok=True)
        
    def export_data(self, data: List[Any], data_type: str, format: str) -> Optional[str]:
        """Экспортировать данные в указанном формате"""
        try:
            # Преобразуем данные в DataFrame
            df = pd.DataFrame([self._convert_to_dict(item) for item in data])
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{data_type}_{timestamp}"
            
            # Экспортируем в выбранном формате
            if format.lower() == 'csv':
                output_path = os.path.join(self.output_dir, f"{filename}.csv")
                df.to_csv(output_path, index=False)
                
            elif format.lower() == 'json':
                output_path = os.path.join(self.output_dir, f"{filename}.json")
                df.to_json(output_path, orient='records')
                
            elif format.lower() == 'parquet':
                output_path = os.path.join(self.output_dir, f"{filename}.parquet")
                df.to_parquet(output_path)
                
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")
                
            self.logger.info(f"Exported {data_type} data to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return None
            
    def _convert_to_dict(self, item: Any) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        if isinstance(item, (GameEvent, PlayerAction, PerformanceMetrics)):
            return {
                key: value for key, value in item.__dict__.items()
                if not key.startswith('_')
            }
        return item 