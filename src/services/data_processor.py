from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from src.models.mongodb_models import Stream, Channel, ViewerHistory, StreamAnalytics
from src.core.youtube_client import YouTubeClient
from src.core.logger import logger
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

class DataProcessor:
    """
    Servicio para procesar y almacenar datos de streams y canales.
    Maneja la lógica de procesamiento de datos en tiempo real y promedios.
    """
    
    def __init__(self):
        load_dotenv()
        self.youtube_client = YouTubeClient()
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client.stream_views
        
        # Colecciones
        self.streams = self.db.streams
        self.channels = self.db.channels
        self.viewer_history = self.db.viewer_history
        self.stream_analytics = self.db.stream_analytics
        
        # Configuración
        self.raw_data_interval = 30  # segundos
        self.average_interval = 5    # minutos
        self.channel_update_interval = 24  # horas

    async def start_processing(self, stream_id: str):
        """
        Inicia el procesamiento de datos para un stream específico.
        """
        try:
            logger.info(f"Iniciando procesamiento para stream {stream_id}")
            
            # Verificar si el stream existe
            stream = await self.streams.find_one({"stream_id": stream_id})
            if not stream:
                logger.error(f"Stream {stream_id} no encontrado")
                return
            
            # Iniciar tareas de procesamiento
            await asyncio.gather(
                self._process_raw_data(stream_id),
                self._process_averages(stream_id),
                self._update_channel_data(stream["channel_id"])
            )
            
        except Exception as e:
            logger.error(f"Error al iniciar procesamiento para stream {stream_id}: {str(e)}")

    async def _process_raw_data(self, stream_id: str):
        """
        Procesa y almacena datos crudos cada 30 segundos.
        """
        while True:
            try:
                # Obtener datos del stream
                stream_data = self.youtube_client.get_stream_details(stream_id)
                if not stream_data:
                    logger.warning(f"No se pudieron obtener datos para stream {stream_id}")
                    await asyncio.sleep(self.raw_data_interval)
                    continue

                # Crear registro de viewers
                viewer_history = ViewerHistory(
                    stream_id=stream_id,
                    channel_id=stream_data["channel_details"]["id"],
                    viewer_count=stream_data["current_viewers"],
                    timestamp=datetime.utcnow(),
                    period_type="raw"
                )

                # Guardar en la base de datos
                await self.viewer_history.insert_one(viewer_history.dict(by_alias=True))
                
                # Actualizar datos del stream
                await self.streams.update_one(
                    {"stream_id": stream_id},
                    {
                        "$set": {
                            "current_viewers": stream_data["current_viewers"],
                            "last_updated": datetime.utcnow()
                        }
                    }
                )

                logger.debug(f"Datos crudos guardados para stream {stream_id}")
                await asyncio.sleep(self.raw_data_interval)

            except Exception as e:
                logger.error(f"Error al procesar datos crudos para stream {stream_id}: {str(e)}")
                await asyncio.sleep(self.raw_data_interval)

    async def _process_averages(self, stream_id: str):
        """
        Calcula y almacena promedios cada 5 minutos.
        """
        while True:
            try:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(minutes=self.average_interval)

                # Obtener datos crudos del período
                cursor = self.viewer_history.find({
                    "stream_id": stream_id,
                    "timestamp": {
                        "$gte": start_time,
                        "$lt": end_time
                    },
                    "period_type": "raw"
                })
                
                viewers = await cursor.to_list(length=None)
                
                if viewers:
                    # Calcular estadísticas
                    viewer_counts = [v["viewer_count"] for v in viewers]
                    avg_viewers = sum(viewer_counts) / len(viewer_counts)
                    peak_viewers = max(viewer_counts)

                    # Crear registro de analytics
                    analytics = StreamAnalytics(
                        stream_id=stream_id,
                        channel_id=viewers[0]["channel_id"],
                        period_start=start_time,
                        period_end=end_time,
                        average_viewers=avg_viewers,
                        peak_viewers=peak_viewers,
                        total_duration=self.average_interval * 60,  # en segundos
                        period_type="5min"
                    )

                    # Guardar en la base de datos
                    await self.stream_analytics.insert_one(analytics.dict(by_alias=True))
                    logger.info(f"Promedios calculados para stream {stream_id}")

                await asyncio.sleep(self.average_interval * 60)

            except Exception as e:
                logger.error(f"Error al procesar promedios para stream {stream_id}: {str(e)}")
                await asyncio.sleep(self.average_interval * 60)

    async def _update_channel_data(self, channel_id: str):
        """
        Actualiza datos del canal cada 24 horas.
        """
        while True:
            try:
                # Obtener datos del canal
                channel_data = self.youtube_client.get_channel_details(channel_id)
                if not channel_data:
                    logger.warning(f"No se pudieron obtener datos para canal {channel_id}")
                    await asyncio.sleep(self.channel_update_interval * 3600)
                    continue

                # Crear objeto Channel
                channel = Channel(
                    channel_id=channel_id,
                    channel_name=channel_data["title"],
                    description=channel_data.get("description"),
                    thumbnail_url=channel_data["thumbnails"].get("default", {}).get("url"),
                    subscriber_count=channel_data["subscriber_count"],
                    view_count=channel_data["view_count"],
                    video_count=channel_data["video_count"],
                    last_updated=datetime.utcnow()
                )

                # Actualizar en la base de datos
                await self.channels.update_one(
                    {"channel_id": channel_id},
                    {"$set": channel.dict(by_alias=True)},
                    upsert=True
                )

                logger.info(f"Datos del canal {channel_id} actualizados")
                await asyncio.sleep(self.channel_update_interval * 3600)

            except Exception as e:
                logger.error(f"Error al actualizar datos del canal {channel_id}: {str(e)}")
                await asyncio.sleep(self.channel_update_interval * 3600)

    async def get_stream_analytics(self, stream_id: str, 
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 period_type: str = "5min") -> List[Dict]:
        """
        Obtiene análisis de un stream en un período específico.
        """
        try:
            query = {
                "stream_id": stream_id,
                "period_type": period_type
            }

            if start_time and end_time:
                query["period_start"] = {
                    "$gte": start_time,
                    "$lte": end_time
                }

            cursor = self.stream_analytics.find(query).sort("period_start", 1)
            return await cursor.to_list(length=None)

        except Exception as e:
            logger.error(f"Error al obtener análisis para stream {stream_id}: {str(e)}")
            return []

    async def get_channel_history(self, channel_id: str,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> List[Dict]:
        """
        Obtiene el historial de streams de un canal.
        """
        try:
            query = {"channel_id": channel_id}
            
            if start_time and end_time:
                query["timestamp"] = {
                    "$gte": start_time,
                    "$lte": end_time
                }

            cursor = self.viewer_history.find(query).sort("timestamp", 1)
            return await cursor.to_list(length=None)

        except Exception as e:
            logger.error(f"Error al obtener historial para canal {channel_id}: {str(e)}")
            return [] 