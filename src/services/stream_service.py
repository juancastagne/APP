from typing import Dict, List, Optional
from src.models.stream_metrics import StreamMetrics, Stream
from src.core.youtube_client import YouTubeClient
from datetime import datetime, timedelta
from src.core.security import security_manager, require_api_key, rate_limit
from src.core.logger import logger
from src.repositories.stream_repository import StreamRepository
from src.repositories.database import Database

class StreamService:
    """
    Servicio para manejar la lógica de negocio relacionada con los streams.
    
    Este servicio implementa medidas de seguridad y validación de datos.
    """
    
    def __init__(self):
        """Inicializa el servicio de streams."""
        self.youtube_client = YouTubeClient()
        self.monitored_streams: Dict[str, StreamMetrics] = {}
        self.last_video_update: Dict[str, datetime] = {}
        self.last_channel_update: Dict[str, datetime] = {}
        self.db = Database()
        self.repository = StreamRepository(self.db)

    @require_api_key
    @rate_limit
    def add_stream(self, video_id: str) -> Optional[Stream]:
        """
        Agrega un nuevo stream para monitorear.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            Optional[Stream]: Stream agregado o None si hay error
        """
        try:
            # Validar y sanitizar el ID del video
            if not security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de agregar stream con ID inválido: {video_id}")
                return None
            
            # Verificar si el stream ya existe
            existing_stream = self.repository.get_stream_by_id(video_id)
            if existing_stream:
                logger.info(f"Stream {video_id} ya existe en la base de datos")
                return existing_stream
            
            # Verificar que el video existe y está en vivo
            video_details = self.youtube_client.get_stream_details_old(video_id)
            if not video_details:
                logger.warning(f"No se pudo obtener información del video {video_id}")
                return None
                
            # Crear nuevo stream con la información obtenida
            stream = Stream(
                video_id=video_id,
                title=video_details.get('title', 'Sin título'),
                channel_name=video_details.get('channel_title', 'Sin canal'),
                thumbnail_url=video_details.get('thumbnail_url', ''),
                current_viewers=video_details.get('current_viewers', 0),
                last_updated=datetime.now()
            )
            
            self.repository.save_stream(stream)
            logger.info(f"Stream {video_id} agregado exitosamente")
            return stream
            
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

    def get_all_streams(self) -> List[Stream]:
        """
        Obtiene todos los streams monitoreados.
        
        Returns:
            List[Stream]: Lista de streams
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
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            # Validar el ID del video
            if not security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de eliminar stream con ID inválido: {video_id}")
                return False
            
            stream = self.repository.get_stream_by_id(video_id)
            if not stream:
                logger.warning(f"Stream {video_id} no encontrado para eliminar")
                return False
            
            self.repository.delete_stream(stream)
            logger.info(f"Stream {video_id} eliminado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar stream {video_id}: {str(e)}")
            return False 