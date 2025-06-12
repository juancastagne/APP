from typing import List, Optional, Dict
from datetime import datetime
import logging
from .database import Database

logger = logging.getLogger(__name__)

class StreamRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_stream(self, video_id: str, session_id: str, title: str, channel_id: str,
                     channel_title: str, thumbnail_url: str, **kwargs) -> Optional[int]:
        """Crea un nuevo stream en la base de datos"""
        try:
            self.db.cursor.execute("""
                INSERT INTO streams (
                    video_id, session_id, title, channel_id, channel_title,
                    thumbnail_url, start_time, status, privacy, license,
                    embeddable, public_stats_viewable, made_for_kids
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id, session_id, title, channel_id, channel_title,
                thumbnail_url, kwargs.get('start_time'), kwargs.get('status'),
                kwargs.get('privacy'), kwargs.get('license'), kwargs.get('embeddable'),
                kwargs.get('public_stats_viewable'), kwargs.get('made_for_kids')
            ))
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error al crear stream: {str(e)}")
            return None

    def update_stream(self, stream_id: int, **kwargs) -> bool:
        """Actualiza los datos de un stream"""
        try:
            update_fields = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return True

            values.append(stream_id)
            query = f"""
                UPDATE streams 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            self.db.cursor.execute(query, values)
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al actualizar stream {stream_id}: {str(e)}")
            return False

    def save_stream_metrics(self, stream_id: int, metrics: Dict) -> bool:
        """Guarda las métricas de un stream"""
        try:
            self.db.cursor.execute("""
                INSERT INTO stream_metrics (
                    stream_id, current_viewers, total_views, like_count,
                    comment_count, live_chat_messages, subscriber_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                stream_id,
                metrics.get('current_viewers'),
                metrics.get('total_views'),
                metrics.get('like_count'),
                metrics.get('comment_count'),
                metrics.get('live_chat_messages'),
                metrics.get('subscriber_count')
            ))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al guardar métricas del stream {stream_id}: {str(e)}")
            return False

    def get_stream_by_session_id(self, session_id: str) -> Optional[Dict]:
        """Obtiene un stream por su session_id"""
        try:
            self.db.cursor.execute("""
                SELECT * FROM streams WHERE session_id = ?
            """, (session_id,))
            row = self.db.cursor.fetchone()
            if row:
                columns = [description[0] for description in self.db.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error al obtener stream con session_id {session_id}: {str(e)}")
            return None

    def get_stream_metrics_history(self, stream_id: int, hours: int = 24) -> List[Dict]:
        """Obtiene el historial de métricas de un stream"""
        try:
            start_time = datetime.now() - datetime.timedelta(hours=hours)
            self.db.cursor.execute("""
                SELECT * FROM stream_metrics 
                WHERE stream_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (stream_id, start_time))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener historial de métricas del stream {stream_id}: {str(e)}")
            return []

    def get_active_streams(self) -> List[Dict]:
        """Obtiene los streams activos"""
        try:
            self.db.cursor.execute("""
                SELECT s.*, sm.current_viewers, sm.total_views, sm.like_count,
                       sm.comment_count, sm.live_chat_messages, sm.subscriber_count
                FROM streams s
                LEFT JOIN stream_metrics sm ON s.id = sm.stream_id
                WHERE s.status = 'live'
                ORDER BY sm.timestamp DESC
            """)
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener streams activos: {str(e)}")
            return []

    def get_all_streams(self) -> List[Dict]:
        """Obtiene todos los streams de la base de datos"""
        try:
            self.db.cursor.execute("""
                SELECT s.*, 
                       COALESCE(sm.current_viewers, 0) as current_viewers,
                       COALESCE(sm.total_views, 0) as total_views,
                       COALESCE(sm.like_count, 0) as like_count,
                       COALESCE(sm.comment_count, 0) as comment_count,
                       COALESCE(sm.live_chat_messages, 0) as live_chat_messages,
                       COALESCE(sm.subscriber_count, 0) as subscriber_count
                FROM streams s
                LEFT JOIN (
                    SELECT stream_id, 
                           current_viewers,
                           total_views,
                           like_count,
                           comment_count,
                           live_chat_messages,
                           subscriber_count,
                           ROW_NUMBER() OVER (PARTITION BY stream_id ORDER BY timestamp DESC) as rn
                    FROM stream_metrics
                ) sm ON s.id = sm.stream_id AND sm.rn = 1
                ORDER BY s.created_at DESC
            """)
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener todos los streams: {str(e)}")
            return [] 