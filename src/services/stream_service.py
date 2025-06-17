from typing import Dict, List, Optional
from src.models.stream_metrics import StreamMetrics, Stream
from src.core.youtube_client import YouTubeClient
from datetime import datetime, timedelta
from src.core.security import security_manager, require_api_key, rate_limit
from src.core.logger import logger
from src.core.database import Database
from bson import ObjectId
import asyncio
import nest_asyncio

# Aplicar parche para permitir anidar bucles de eventos
nest_asyncio.apply()

class StreamService:
    """
    Servicio para manejar la lógica de negocio relacionada con los streams.
    
    Este servicio implementa medidas de seguridad y validación de datos.
    """
    
    def __init__(self):
        """Inicializa el servicio de streams."""
        self.youtube_client = YouTubeClient()
        self.security_manager = security_manager
        self.db = Database.db
        self._loop = None

    def _get_loop(self):
        """Obtiene o crea un bucle de eventos."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    def get_all_streams(self) -> List[Stream]:
        """
        Obtiene todos los streams activos.
        
        Returns:
            List[Stream]: Lista de streams activos
        """
        try:
            loop = self._get_loop()
            cursor = self.db.streams.find()
            streams = []
            
            # Convertir el cursor a una lista de documentos
            docs = loop.run_until_complete(cursor.to_list(length=None))
            
            # Convertir los documentos a objetos Stream
            for doc in docs:
                streams.append(Stream(**doc))
            
            return streams
        except Exception as e:
            logger.error(f"Error al obtener streams: {str(e)}")
            return []

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
            if not self.security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de obtener detalles de stream con ID inválido: {video_id}")
                return None
            
            # Ejecutar la operación asíncrona en un bucle de eventos
            loop = self._get_loop()
            stream_data = loop.run_until_complete(
                self.db.streams.find_one({"video_id": video_id})
            )
            
            if stream_data:
                return Stream(**stream_data)
            return None
        except Exception as e:
            logger.error(f"Error al obtener detalles del stream {video_id}: {str(e)}")
            return None

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
            existing_stream = self.get_stream_details(video_id)
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
                channel_name=video_details.get('channel_title', 'Sin canal'),
                thumbnail_url=video_details.get('thumbnail_url', ''),
                current_viewers=video_details.get('current_viewers', 0)
            )
            
            # Guardar el stream
            loop = self._get_loop()
            result = loop.run_until_complete(
                self.db.streams.insert_one(stream.model_dump(by_alias=True))
            )
            stream.id = result.inserted_id
            return stream
            
        except Exception as e:
            logger.error(f"Error al agregar stream {video_id}: {str(e)}")
            return None

    def remove_stream(self, video_id: str) -> bool:
        """Elimina un stream del monitoreo"""
        try:
            loop = self._get_loop()
            result = loop.run_until_complete(
                self.db.streams.delete_one({"video_id": video_id})
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar stream {video_id}: {str(e)}")
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
            if not self.security_manager.validate_video_id(video_id):
                logger.warning(f"Intento de actualizar stream con ID inválido: {video_id}")
                return None
            
            # Obtener stream actual
            stream = self.get_stream_details(video_id)
            if not stream:
                logger.warning(f"Stream {video_id} no encontrado")
                return None
            
            # Obtener métricas actualizadas
            video_details = self.youtube_client.get_stream_details_old(video_id)
            if not video_details:
                logger.error(f"No se pudieron obtener los detalles del video {video_id}")
                return None
            
            # Actualizar métricas
            stream.current_viewers = video_details.get('current_viewers', 0)
            stream.last_updated = datetime.now()
            
            # Guardar cambios
            loop = self._get_loop()
            loop.run_until_complete(
                self.db.streams.update_one(
                    {"video_id": video_id},
                    {"$set": stream.model_dump(by_alias=True)}
                )
            )
            
            return stream
            
        except Exception as e:
            logger.error(f"Error al actualizar métricas del stream {video_id}: {str(e)}")
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
                stream_id=video_id,
                concurrent_viewers=video_details.get('current_viewers', 0),
                total_views=video_details.get('total_views', 0),
                like_count=video_details.get('like_count', 0),
                comment_count=video_details.get('comment_count', 0),
                live_chat_messages=video_details.get('live_chat_messages', 0),
                subscriber_count=video_details.get('subscriber_count', 0)
            )
            
            # Guardar métricas
            loop = self._get_loop()
            loop.run_until_complete(
                self.db.stream_metrics.insert_one(metrics.model_dump(by_alias=True))
            )
            
            return {
                'current_viewers': metrics.concurrent_viewers,
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

    def delete_stream(self, video_id: str) -> bool:
        """
        Elimina un stream del monitoreo.
        
        Args:
            video_id (str): ID del video de YouTube
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            result = self.db.streams.delete_one({"video_id": video_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar stream {video_id}: {str(e)}")
            return False 