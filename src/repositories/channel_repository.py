from typing import List, Optional, Dict
from datetime import datetime
import logging
from .database import Database

logger = logging.getLogger(__name__)

class ChannelRepository:
    def __init__(self, db: Database):
        self.db = db

    def save_channel_metrics(self, channel_id: str, metrics: Dict) -> bool:
        """Guarda las métricas de un canal"""
        try:
            self.db.cursor.execute("""
                INSERT INTO channel_metrics (
                    channel_id, subscriber_count, video_count, view_count
                ) VALUES (?, ?, ?, ?)
            """, (
                channel_id,
                metrics.get('subscriber_count'),
                metrics.get('video_count'),
                metrics.get('view_count')
            ))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al guardar métricas del canal {channel_id}: {str(e)}")
            return False

    def get_channel_metrics_history(self, channel_id: str, hours: int = 24) -> List[Dict]:
        """Obtiene el historial de métricas de un canal"""
        try:
            start_time = datetime.now() - datetime.timedelta(hours=hours)
            self.db.cursor.execute("""
                SELECT * FROM channel_metrics 
                WHERE channel_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (channel_id, start_time))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener historial de métricas del canal {channel_id}: {str(e)}")
            return []

    def get_latest_channel_metrics(self, channel_id: str) -> Optional[Dict]:
        """Obtiene las últimas métricas de un canal"""
        try:
            self.db.cursor.execute("""
                SELECT * FROM channel_metrics 
                WHERE channel_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (channel_id,))
            
            row = self.db.cursor.fetchone()
            if row:
                columns = [description[0] for description in self.db.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error al obtener últimas métricas del canal {channel_id}: {str(e)}")
            return None

    def get_channels_by_viewer_count(self, min_viewers: int = 0) -> List[Dict]:
        """Obtiene canales ordenados por cantidad de viewers"""
        try:
            self.db.cursor.execute("""
                SELECT DISTINCT s.channel_id, s.channel_title, 
                       MAX(sm.current_viewers) as max_viewers,
                       AVG(sm.current_viewers) as avg_viewers
                FROM streams s
                JOIN stream_metrics sm ON s.id = sm.stream_id
                WHERE sm.current_viewers >= ?
                GROUP BY s.channel_id, s.channel_title
                ORDER BY max_viewers DESC
            """, (min_viewers,))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener canales por viewers: {str(e)}")
            return [] 