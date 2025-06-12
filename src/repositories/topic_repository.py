from typing import List, Optional, Dict
from datetime import datetime
import logging
from .database import Database

logger = logging.getLogger(__name__)

class TopicRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_topic(self, name: str, description: Optional[str] = None) -> Optional[int]:
        """Crea un nuevo tópico"""
        try:
            self.db.cursor.execute("""
                INSERT INTO topics (name, description)
                VALUES (?, ?)
            """, (name, description))
            self.db.conn.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error al crear tópico {name}: {str(e)}")
            return None

    def assign_topic_to_stream(self, stream_id: int, topic_id: int, confidence: float) -> bool:
        """Asigna un tópico a un stream con un nivel de confianza"""
        try:
            self.db.cursor.execute("""
                INSERT INTO stream_topics (stream_id, topic_id, confidence)
                VALUES (?, ?, ?)
            """, (stream_id, topic_id, confidence))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al asignar tópico {topic_id} al stream {stream_id}: {str(e)}")
            return False

    def save_topic_metrics(self, topic_id: int, metrics: Dict) -> bool:
        """Guarda las métricas de un tópico"""
        try:
            self.db.cursor.execute("""
                INSERT INTO topic_metrics (
                    topic_id, total_streams, total_viewers,
                    avg_viewers, max_viewers
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                topic_id,
                metrics.get('total_streams'),
                metrics.get('total_viewers'),
                metrics.get('avg_viewers'),
                metrics.get('max_viewers')
            ))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error al guardar métricas del tópico {topic_id}: {str(e)}")
            return False

    def get_topic_by_name(self, name: str) -> Optional[Dict]:
        """Obtiene un tópico por su nombre"""
        try:
            self.db.cursor.execute("""
                SELECT * FROM topics WHERE name = ?
            """, (name,))
            row = self.db.cursor.fetchone()
            if row:
                columns = [description[0] for description in self.db.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error al obtener tópico {name}: {str(e)}")
            return None

    def get_stream_topics(self, stream_id: int) -> List[Dict]:
        """Obtiene los tópicos de un stream"""
        try:
            self.db.cursor.execute("""
                SELECT t.*, st.confidence
                FROM topics t
                JOIN stream_topics st ON t.id = st.topic_id
                WHERE st.stream_id = ?
                ORDER BY st.confidence DESC
            """, (stream_id,))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener tópicos del stream {stream_id}: {str(e)}")
            return []

    def get_topics_by_popularity(self, min_streams: int = 0) -> List[Dict]:
        """Obtiene tópicos ordenados por popularidad"""
        try:
            self.db.cursor.execute("""
                SELECT t.*, 
                       COUNT(DISTINCT st.stream_id) as total_streams,
                       MAX(tm.total_viewers) as max_viewers,
                       AVG(tm.avg_viewers) as avg_viewers
                FROM topics t
                LEFT JOIN stream_topics st ON t.id = st.topic_id
                LEFT JOIN topic_metrics tm ON t.id = tm.topic_id
                GROUP BY t.id
                HAVING total_streams >= ?
                ORDER BY total_streams DESC, max_viewers DESC
            """, (min_streams,))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener tópicos por popularidad: {str(e)}")
            return []

    def get_topic_metrics_history(self, topic_id: int, hours: int = 24) -> List[Dict]:
        """Obtiene el historial de métricas de un tópico"""
        try:
            start_time = datetime.now() - datetime.timedelta(hours=hours)
            self.db.cursor.execute("""
                SELECT * FROM topic_metrics 
                WHERE topic_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (topic_id, start_time))
            
            columns = [description[0] for description in self.db.cursor.description]
            return [dict(zip(columns, row)) for row in self.db.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener historial de métricas del tópico {topic_id}: {str(e)}")
            return [] 