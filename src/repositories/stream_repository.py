from typing import List, Optional, Dict
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from ..models.stream_metrics import Stream, StreamMetrics
from ..core.logger import logger

class StreamRepository:
    """
    Repositorio para manejar las operaciones de base de datos relacionadas con streams.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_stream(self, stream: Stream) -> Stream:
        """
        Crea un nuevo stream en la base de datos.
        
        Args:
            stream (Stream): Objeto Stream a crear
            
        Returns:
            Stream: Stream creado
        """
        try:
            self.db.add(stream)
            self.db.commit()
            self.db.refresh(stream)
            logger.info(f"Stream creado: {stream.video_id}")
            return stream
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear stream: {str(e)}")
            raise

    def update_stream(self, stream: Stream) -> Stream:
        """
        Actualiza un stream existente.
        
        Args:
            stream (Stream): Stream a actualizar
            
        Returns:
            Stream: Stream actualizado
        """
        try:
            self.db.commit()
            self.db.refresh(stream)
            return stream
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar stream {stream.video_id}: {str(e)}")
            raise

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

    def get_all_streams(self) -> List[Stream]:
        """
        Obtiene todos los streams activos.
        
        Returns:
            List[Stream]: Lista de streams activos
        """
        try:
            return self.db.query(Stream).filter(Stream.is_active == True).all()
        except Exception as e:
            logger.error(f"Error al obtener streams: {str(e)}")
            return []

    def get_stream_by_id(self, video_id: str) -> Optional[Stream]:
        """
        Obtiene un stream por su video_id.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Stream]: Stream encontrado o None si no existe
        """
        try:
            return self.db.query(Stream).filter(Stream.video_id == video_id).first()
        except Exception as e:
            logger.error(f"Error al obtener stream {video_id}: {str(e)}")
            return None

    def delete_stream(self, video_id: str) -> bool:
        """
        Elimina un stream por su video_id.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            stream = self.get_stream_by_id(video_id)
            if stream:
                self.db.delete(stream)
                self.db.commit()
                logger.info(f"Stream eliminado: {video_id}")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar stream {video_id}: {str(e)}")
            return False

    def add_metrics(self, metrics: StreamMetrics) -> StreamMetrics:
        """
        Agrega nuevas métricas para un stream.
        
        Args:
            metrics (StreamMetrics): Métricas a agregar
            
        Returns:
            StreamMetrics: Métricas agregadas
        """
        try:
            self.db.add(metrics)
            self.db.commit()
            self.db.refresh(metrics)
            return metrics
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al agregar métricas para stream {metrics.video_id}: {str(e)}")
            raise

    def get_stream_metrics(self, video_id: str, limit: int = 100) -> List[StreamMetrics]:
        """
        Obtiene las métricas históricas de un stream.
        
        Args:
            video_id (str): ID del video de YouTube
            limit (int): Límite de métricas a obtener
            
        Returns:
            List[StreamMetrics]: Lista de métricas
        """
        try:
            return self.db.query(StreamMetrics)\
                .filter(StreamMetrics.video_id == video_id)\
                .order_by(StreamMetrics.timestamp.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error al obtener métricas para stream {video_id}: {str(e)}")
            return [] 