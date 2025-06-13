from nicegui import ui # type: ignore
from src.services.stream_service import StreamService
from src.core.logger import logger
from src.core.database import get_db
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
        self.db = next(get_db())
        self.stream_service = StreamService(self.db)
        self.streams = []
        self.update_timer = None
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
                
                # Lista de streams
                self.streams_container = ui.column().classes('w-full gap-4')
                
                # Cargar streams iniciales
                self.load_streams()
                
                # Configurar actualización automática
                self.update_timer = ui.timer(30.0, self.load_streams)
                
            logger.info("Interfaz de usuario iniciada correctamente")
            
        except Exception as e:
            logger.error(f"Error al configurar la interfaz: {str(e)}")
            raise
    
    def show_add_dialog(self):
        """Muestra el diálogo para agregar un nuevo stream."""
        with ui.dialog() as dialog, ui.card():
            ui.label('Agregar Stream').classes('text-xl font-bold mb-4')
            video_id = ui.input('ID del Video', placeholder='Ingresa el ID del video de YouTube')
            
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancelar', on_click=dialog.close).classes('bg-gray-500 text-white')
                ui.button('Agregar', on_click=lambda: self.add_stream(video_id.value, dialog)).classes('bg-blue-500 text-white')
    
    def add_stream(self, video_id: str, dialog):
        """Agrega un nuevo stream para monitorear."""
        try:
            if not video_id:
                ui.notify('Por favor ingresa un ID de video', type='negative')
                return
            
            stream = self.stream_service.add_stream(video_id)
            if stream:
                ui.notify('Stream agregado correctamente', type='positive')
                dialog.close()
                self.load_streams()
            else:
                ui.notify('No se pudo agregar el stream', type='negative')
                
        except Exception as e:
            logger.error(f"Error al agregar stream: {str(e)}")
            ui.notify('Error al agregar el stream', type='negative')
    
    def load_streams(self):
        """Carga y actualiza la lista de streams."""
        try:
            self.streams = self.stream_service.get_all_streams()
            self.update_streams_display()
        except Exception as e:
            logger.error(f"Error al cargar streams: {str(e)}")
    
    def update_streams_display(self):
        """Actualiza la visualización de los streams."""
        self.streams_container.clear()
        
        for stream in self.streams:
            with self.streams_container:
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('w-full justify-between items-start'):
                        # Información del stream
                        with ui.column().classes('gap-2'):
                            ui.label(stream.title).classes('text-xl font-bold')
                            ui.label(f'Canal: {stream.channel_name}').classes('text-gray-600')
                            ui.label(f'Viewers: {stream.current_viewers:,}').classes('text-green-600 font-semibold')
                        
                        # Botones de acción
                        with ui.row().classes('gap-2'):
                            ui.button('Eliminar', on_click=lambda s=stream: self.delete_stream(s.video_id)).classes('bg-red-500 text-white')
    
    def delete_stream(self, video_id: str):
        """Elimina un stream del monitoreo."""
        try:
            if self.stream_service.delete_stream(video_id):
                ui.notify('Stream eliminado correctamente', type='positive')
                self.load_streams()
            else:
                ui.notify('No se pudo eliminar el stream', type='negative')
        except Exception as e:
            logger.error(f"Error al eliminar stream: {str(e)}")
            ui.notify('Error al eliminar el stream', type='negative')

if __name__ in {"__main__", "__mp_main__"}:
    app = StreamViewerApp()
    app.start() 