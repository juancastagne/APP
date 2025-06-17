from nicegui import ui # type: ignore
from ..core.logger import logger
from ..core.database import Database
from ..services.stream_service import StreamService
from .components.stream_graph import StreamGraph
import asyncio
from datetime import datetime
from collections import defaultdict

# CSS global para diálogos anchos
ui.add_head_html('<style>.q-dialog__inner--minimized, .q-dialog__inner { max-width: 90vw !important; }</style>')

# CSS global para diálogos anchos personalizados
ui.add_head_html('<style>.dialog-ancho { max-width: 90vw !important; min-width: 70vw !important; }</style>')

class StreamViewerApp:
    """
    Aplicación principal para monitorear streams de YouTube.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.stream_service = StreamService()
        self.streams = []
        self.update_timer = None
        self.stream_graph = StreamGraph()
        logger.info("Iniciando aplicación Stream Views")
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        try:
            # Configurar el tema
            ui.query('body').classes('bg-gray-100')
            
            # Contenedor principal
            with ui.column().classes('w-full max-w-7xl mx-auto p-4'):
                # Título y botón de agregar
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Stream Views').classes('text-2xl font-bold')
                    ui.button('Agregar Stream', on_click=self.show_add_dialog).classes('bg-blue-500 text-white')
                
                # Gráfico de streams
                with ui.card().classes('w-full mb-4'):
                    self.stream_graph.plot
                
                # Lista de streams
                self.streams_container = ui.column().classes('w-full gap-4')
                
                # Cargar streams iniciales
                self.load_streams()
                
                # Configurar actualización automática cada 30 segundos
                self.update_timer = ui.timer(30.0, self.load_streams)
                
            logger.info("Interfaz de usuario iniciada correctamente")
            
        except Exception as e:
            logger.error(f"Error al configurar la interfaz: {str(e)}")
            raise
    
    def show_add_dialog(self):
        """Muestra el diálogo para agregar un nuevo stream."""
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-md'):
            ui.label('Agregar Stream').classes('text-xl font-bold mb-4')
            
            # Input para el ID del video
            video_id = ui.input(
                label='ID del Video',
                placeholder='Ingresa el ID del video de YouTube'
            ).classes('w-full mb-4')
            
            # Mensaje de ayuda
            ui.label('El ID del video es la parte final de la URL de YouTube').classes('text-sm text-gray-500 mb-4')
            ui.label('Ejemplo: https://www.youtube.com/watch?v=VIDEO_ID').classes('text-sm text-gray-500 mb-4')
            
            # Botones de acción
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancelar', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('Agregar', on_click=lambda: self.add_stream(video_id.value, dialog)).classes('bg-blue-500 text-white')
        
        dialog.open()
    
    async def add_stream(self, video_id: str, dialog):
        """Agrega un nuevo stream para monitorear."""
        try:
            if not video_id:
                ui.notify('Por favor ingresa un ID de video', type='negative')
                return
            
            # Limpiar el ID del video (eliminar espacios y caracteres no deseados)
            video_id = video_id.strip()
            
            # Validar formato básico del ID
            if len(video_id) < 8 or len(video_id) > 20:
                ui.notify('El ID del video parece inválido', type='negative')
                return
            
            # Intentar agregar el stream
            stream = await self.stream_service.add_stream(video_id)
            
            if stream:
                ui.notify('Stream agregado correctamente', type='positive')
                dialog.close()
                await self.load_streams()  # Recargar la lista de streams
            else:
                ui.notify('No se pudo agregar el stream. Verifica el ID y que el video esté en vivo.', type='negative')
                
        except Exception as e:
            logger.error(f"Error al agregar stream: {str(e)}")
            ui.notify('Error al agregar el stream. Por favor intenta nuevamente.', type='negative')
    
    async def load_streams(self):
        """Carga y actualiza la lista de streams."""
        try:
            # Obtener streams de la base de datos
            self.streams = await self.stream_service.get_all_streams()
            
            # Actualizar métricas de cada stream
            for stream in self.streams:
                updated_stream = await self.stream_service.update_stream_metrics(stream.video_id)
                if updated_stream:
                    stream.current_viewers = updated_stream.current_viewers
                    stream.last_updated = updated_stream.last_updated
                    # Actualizar el gráfico con los nuevos datos
                    self.stream_graph.update_data(
                        stream_id=stream.video_id,
                        viewers=stream.current_viewers,
                        timestamp=stream.last_updated
                    )
            
            # Actualizar la visualización
            self.update_streams_display()
            
            logger.info(f"Streams actualizados: {len(self.streams)}")
            
        except Exception as e:
            logger.error(f"Error al cargar streams: {str(e)}")
    
    def update_streams_display(self):
        """Actualiza la visualización de los streams."""
        self.streams_container.clear()
        
        if not self.streams:
            with self.streams_container:
                ui.label('No hay streams monitoreados').classes('text-gray-500 text-center p-4')
            return
        
        for stream in self.streams:
            with self.streams_container:
                with ui.card().classes('w-full p-4 hover:shadow-lg transition-shadow'):
                    with ui.row().classes('w-full justify-between items-start gap-4'):
                        # Thumbnail del video
                        if stream.thumbnail_url:
                            ui.image(stream.thumbnail_url).classes('w-48 h-27 object-cover rounded')
                        
                        # Información del stream
                        with ui.column().classes('flex-grow gap-2'):
                            ui.label(stream.title).classes('text-xl font-bold')
                            ui.label(stream.channel_name).classes('text-gray-600')
                            
                            # Métricas
                            with ui.row().classes('gap-4 mt-2'):
                                with ui.column().classes('items-center'):
                                    ui.label('👥').classes('text-2xl')
                                    ui.label(f'{stream.current_viewers:,}').classes('text-green-600 font-semibold')
                                    ui.label('Viewers').classes('text-sm text-gray-500')
                                
                                with ui.column().classes('items-center'):
                                    ui.label('⏱️').classes('text-2xl')
                                    ui.label(stream.last_updated.strftime('%H:%M:%S')).classes('text-blue-600 font-semibold')
                                    ui.label('Última actualización').classes('text-sm text-gray-500')
                        
                        # Botones de acción
                        with ui.column().classes('gap-2'):
                            ui.button(
                                'Más detalles',
                                on_click=lambda s=stream: self.show_stream_details(s)
                            ).props('flat').classes('text-blue-500')
                            
                            ui.button(
                                icon='refresh',
                                on_click=lambda s=stream: self.refresh_stream(s.video_id)
                            ).props('flat').classes('text-blue-500')
                            
                            ui.button(
                                icon='delete',
                                on_click=lambda s=stream: self.delete_stream(s.video_id)
                            ).props('flat').classes('text-red-500')
    
    async def refresh_stream(self, video_id: str):
        """Actualiza manualmente un stream específico."""
        try:
            stream = await self.stream_service.update_stream_metrics(video_id)
            if stream:
                ui.notify('Stream actualizado correctamente', type='positive')
                await self.load_streams()
            else:
                ui.notify('No se pudo actualizar el stream', type='negative')
        except Exception as e:
            logger.error(f"Error al actualizar stream: {str(e)}")
            ui.notify('Error al actualizar el stream', type='negative')
    
    async def delete_stream(self, video_id: str):
        """Elimina un stream del monitoreo."""
        try:
            if await self.stream_service.delete_stream(video_id):
                ui.notify('Stream eliminado correctamente', type='positive')
                await self.load_streams()
            else:
                ui.notify('No se pudo eliminar el stream', type='negative')
        except Exception as e:
            logger.error(f"Error al eliminar stream: {str(e)}")
            ui.notify('Error al eliminar el stream', type='negative')

    def update_metrics(self):
        """Actualiza las métricas de los streams actuales."""
        try:
            for stream in self.streams:
                updated_stream = self.stream_service.update_stream_metrics(stream.video_id)
                if updated_stream:
                    # Actualizar el stream en la lista
                    stream.current_viewers = updated_stream.current_viewers
                    stream.last_updated = updated_stream.last_updated
            
            # Actualizar la visualización
            self.update_streams_display()
            
        except Exception as e:
            logger.error(f"Error al actualizar métricas: {str(e)}")

    def show_stream_details(self, stream):
        """Muestra los detalles completos de un stream."""
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-2xl'):
            ui.label('Detalles del Stream').classes('text-xl font-bold mb-4')
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Información básica
                with ui.column().classes('gap-2'):
                    ui.label('Información Básica').classes('text-lg font-semibold')
                    ui.label(f'Título: {stream.title}')
                    ui.label(f'Canal: {stream.channel_name}')
                    ui.label(f'Estado: {"Activo" if stream.is_active else "Inactivo"}')
                    ui.label(f'Creado: {stream.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
                    ui.label(f'Última actualización: {stream.last_updated.strftime("%Y-%m-%d %H:%M:%S")}')
                
                # Métricas actuales
                with ui.column().classes('gap-2'):
                    ui.label('Métricas Actuales').classes('text-lg font-semibold')
                    ui.label(f'Viewers actuales: {stream.current_viewers:,}')
                    
                    # Obtener métricas adicionales
                    metrics = self.stream_service.get_stream_metrics(stream.video_id, limit=1)
                    if metrics:
                        latest_metrics = metrics[0]
                        ui.label(f'Total de vistas: {latest_metrics.total_views:,}')
                        ui.label(f'Likes: {latest_metrics.like_count:,}')
                        ui.label(f'Comentarios: {latest_metrics.comment_count:,}')
                        ui.label(f'Mensajes en chat: {latest_metrics.live_chat_messages:,}')
                        ui.label(f'Suscriptores: {latest_metrics.subscriber_count:,}')
            
            # Botón para cerrar
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cerrar', on_click=dialog.close).classes('bg-blue-500 text-white')
        
        dialog.open()

    def start(self):
        """Inicia la aplicación."""
        try:
            self.setup_ui()
            ui.run(
                title='Stream Views',
                favicon='🎥',
                port=8080,
                host='0.0.0.0'
            )
        except Exception as e:
            logger.error(f"Error al iniciar la aplicación: {str(e)}")
            raise

if __name__ in {"__main__", "__mp_main__"}:
    app = StreamViewerApp()
    app.start() 