from typing import Dict, List, Optional
from src.models.stream_metrics import StreamMetrics, Stream
from src.core.youtube_client import YouTubeClient
from datetime import datetime, timedelta
from src.core.security import security_manager, require_api_key, rate_limit
from src.core.logger import logger
from src.repositories.stream_repository import StreamRepository
from sqlalchemy.orm import Session
from src.core.security import SecurityManager

class StreamService:
    """
    Servicio para manejar la lógica de negocio relacionada con los streams.
    
    Este servicio implementa medidas de seguridad y validación de datos.
    """
    
    def __init__(self, db_session: Session):
        """Inicializa el servicio de streams."""
        self.repository = StreamRepository(db_session)
        self.youtube_client = YouTubeClient()
        self.security_manager = SecurityManager()

    @require_api_key
    @rate_limit
    def add_stream(self, video_id: str) -> Optional[Stream]:
        """
        Agrega un nuevo stream para monitorear.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Stream]: Stream agregado o None si hubo un error
        """
        try:
            # Validar el video_id
            if not self.security_manager.validate_video_id(video_id):
                logger.error(f"Video ID inválido: {video_id}")
                return None
            
            # Verificar si el stream ya existe
            existing_stream = self.repository.get_stream_by_id(video_id)
            if existing_stream:
                logger.warning(f"El stream {video_id} ya está siendo monitoreado")
                return existing_stream
            
            # Obtener detalles del video
            video_details = self.youtube_client.get_stream_details_old(video_id)
            if not video_details:
                logger.error(f"No se pudieron obtener los detalles del video {video_id}")
                return None
            
            # Crear el stream
            stream = Stream(
                video_id=video_id,
                title=video_details.get('title', 'Sin título'),
                channel_name=video_details.get('channel_name', 'Sin canal'),
                thumbnail_url=video_details.get('thumbnail_url', ''),
                current_viewers=video_details.get('current_viewers', 0)
            )
            
            # Guardar el stream
            return self.repository.create_stream(stream)
            
        except Exception as e:
            logger.error(f"Error al agregar stream {video_id}: {str(e)}")
            return None

    def remove_stream(self, video_id: str) -> bool:
        """Elimina un stream del monitoreo"""
        if video_id in self.monitored_streams:
            del self.monitored_streams[video_id]
            return True
        return False

    @require_api_key
    @rate_limit
    def update_stream_metrics(self, video_id: str) -> Optional[Stream]:
        """
        Actualiza las métricas de un stream.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Stream]: Stream actualizado o None si hay error
        """
        try:
            # Validar el ID del video
            if not security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de actualizar stream con ID inválido: {video_id}")
                return None
            
            # Obtener stream actual
            stream = self.repository.get_stream_by_id(video_id)
            if not stream:
                logger.warning(f"Stream {video_id} no encontrado")
                return None
            
            # Actualizar métricas
            # Aquí iría la lógica de actualización de métricas
            # Por ahora solo actualizamos el timestamp
            stream.last_updated = datetime.now()
            self.repository.save_stream(stream)
            
            logger.debug(f"Métricas del stream {video_id} actualizadas")
            return stream
            
        except Exception as e:
            logger.error(f"Error al actualizar métricas del stream {video_id}: {str(e)}")
            return None

    def get_stream_details(self, video_id: str) -> Optional[Stream]:
        """
        Obtiene los detalles de un stream específico.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Stream]: Stream encontrado o None si no existe
        """
        try:
            # Validar el ID del video
            if not security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de obtener detalles de stream con ID inválido: {video_id}")
                return None
            
            return self.repository.get_stream_by_id(video_id)
        except Exception as e:
            logger.error(f"Error al obtener detalles del stream {video_id}: {str(e)}")
            return None

    def get_stream_metrics(self, video_id: str) -> Optional[Dict]:
        """
        Obtiene las métricas actuales de un stream.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Dict]: Métricas del stream o None si hubo un error
        """
        try:
            # Obtener detalles del video
            video_details = self.youtube_client.get_stream_details_old(video_id)
            if not video_details:
                return None
            
            # Crear métricas
            metrics = StreamMetrics(
                video_id=video_id,
                current_viewers=video_details.get('current_viewers', 0),
                total_views=video_details.get('total_views', 0),
                like_count=video_details.get('like_count', 0),
                comment_count=video_details.get('comment_count', 0),
                live_chat_messages=video_details.get('live_chat_messages', 0),
                subscriber_count=video_details.get('subscriber_count', 0),
                additional_metrics=video_details
            )
            
            # Guardar métricas
            self.repository.add_metrics(metrics)
            
            return {
                'current_viewers': metrics.current_viewers,
                'total_views': metrics.total_views,
                'like_count': metrics.like_count,
                'comment_count': metrics.comment_count,
                'live_chat_messages': metrics.live_chat_messages,
                'subscriber_count': metrics.subscriber_count,
                'timestamp': metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error al obtener métricas para stream {video_id}: {str(e)}")
            return None

    def get_all_streams(self) -> List[Stream]:
        """
        Obtiene todos los streams activos.
        
        Returns:
            List[Stream]: Lista de streams activos
        """
        try:
            return self.repository.get_all_streams()
        except Exception as e:
            logger.error(f"Error al obtener streams: {str(e)}")
            return []

    def delete_stream(self, video_id: str) -> bool:
        """
        Elimina un stream del monitoreo.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            return self.repository.delete_stream(video_id)
        except Exception as e:
            logger.error(f"Error al eliminar stream {video_id}: {str(e)}")
            return False 