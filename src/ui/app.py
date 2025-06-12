from nicegui import ui # type: ignore
from src.services.stream_service import StreamService
from src.core.logger import logger
import asyncio
from datetime import datetime
from collections import defaultdict

# CSS global para diálogos anchos
ui.add_head_html('<style>.q-dialog__inner--minimized, .q-dialog__inner { max-width: 90vw !important; }</style>')

# CSS global para diálogos anchos personalizados
ui.add_head_html('<style>.dialog-ancho { max-width: 90vw !important; min-width: 70vw !important; }</style>')

class StreamViewerApp:
    """
    Aplicación principal para monitorear streams de YouTube en tiempo real.
    
    Esta clase maneja la interfaz de usuario y la lógica principal de la aplicación,
    permitiendo monitorear múltiples streams simultáneamente y visualizar sus métricas.
    
    Attributes:
        stream_service (StreamService): Servicio para interactuar con la API de YouTube
        stream_cards (dict): Diccionario que mapea IDs de video a sus tarjetas UI
        historical_data (defaultdict): Datos históricos de visualizadores por stream
        main_chart: Gráfico principal para visualizar tendencias
    """

    def __init__(self):
        """
        Inicializa la aplicación Stream Views.
        Configura los servicios necesarios y la interfaz de usuario.
        """
        logger.info("Iniciando aplicación Stream Views")
        try:
            # Inicializar servicios
            self.stream_service = StreamService()
            
            # Configurar la interfaz
            self.setup_ui()
            logger.info("Aplicación inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar la aplicación: {str(e)}")
            raise

    def setup_ui(self):
        """Configura la interfaz de usuario principal."""
        try:
            with ui.column().classes('w-full max-w-7xl mx-auto p-4'):
                # Título
                ui.label('Stream Views').classes('text-3xl font-bold mb-8')
                
                # Gráfico principal
                self.main_chart = ui.echart({
                    'title': {'text': 'Visualizadores en Tiempo Real'},
                    'tooltip': {'trigger': 'axis'},
                    'legend': {'data': [], 'bottom': 0},
                    'xAxis': {
                        'type': 'category',
                        'data': [],
                        'name': 'Hora',
                        'nameLocation': 'middle',
                        'nameGap': 30
                    },
                    'yAxis': {
                        'type': 'value',
                        'name': 'Visualizadores',
                        'position': 'left'
                    },
                    'series': []
                }).classes('w-full h-96')
                
                # Contenedor de tarjetas de streams
                self.streams_container = ui.column().classes('w-full gap-4')
            
            # Configurar actualizaciones periódicas
            ui.timer(10.0, self.update_streams)
            
            logger.info("Interfaz de usuario iniciada correctamente")
            
        except Exception as e:
            logger.error(f"Error al iniciar la interfaz de usuario: {str(e)}")
            raise

    def create_stream_card(self, stream):
        """
        Crea una tarjeta visual para un stream con sus métricas principales.
        
        Args:
            stream (Stream): Objeto que contiene la información del stream
        """
        with ui.card().classes('w-full hover:shadow-lg transition-shadow duration-300') as card:
            with ui.row().classes('w-full items-center gap-4 p-4'):
                # Thumbnail
                ui.image(stream.thumbnail_url).classes('w-48 h-27 rounded-lg')
                
                # Contenido principal y botón en la misma fila
                with ui.row().classes('flex-grow w-full items-center justify-between'):
                    # Columna de info
                    with ui.column().classes('gap-1'):
                        ui.label(stream.title).classes('text-lg font-bold')
                        ui.label(stream.channel_title).classes('text-sm text-gray-600')
                        # Métricas en tiempo real
                        with ui.row().classes('gap-4 mt-2'):
                            with ui.column().classes('items-center'):
                                ui.label('👥').classes('text-2xl')
                                ui.label(f"{stream.subscriber_count:,}").classes('text-sm font-semibold')
                            with ui.column().classes('items-center'):
                                ui.label('👍').classes('text-2xl')
                                ui.label(f"{stream.like_count:,}").classes('text-sm font-semibold')
                            with ui.column().classes('items-center'):
                                ui.label('💬').classes('text-2xl')
                                ui.label(f"{stream.live_chat_messages:,}").classes('text-sm font-semibold')
                    # Botón alineado a la derecha
                    ui.button('Ver Detalles', on_click=lambda: self.show_stream_details(stream)).classes('bg-blue-500 text-white')
            self.stream_cards[stream.video_id] = card

    def show_stream_details(self, stream):
        """
        Muestra un diálogo con información detallada del stream.
        
        Args:
            stream (Stream): Objeto que contiene la información del stream
        """
        with ui.dialog().classes('dialog-ancho') as dialog, ui.card().classes('dialog-ancho p-8'):
            with ui.column().classes('w-full gap-4 p-4'):
                # Encabezado con miniatura
                with ui.row().classes('w-full items-center gap-4'):
                    ui.image(stream.thumbnail_url).classes('w-48 h-27 rounded-lg')
                    with ui.column():
                        ui.label(stream.title).classes('text-xl font-bold')
                        ui.label(stream.channel_title).classes('text-lg text-gray-600')
                
                # Información del video
                with ui.card().classes('w-full'):
                    ui.label('Información del Video').classes('text-lg font-bold mb-2')
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        ui.label('ID del Video:').classes('font-semibold')
                        ui.label(stream.video_id)
                        
                        ui.label('Descripción:').classes('font-semibold')
                        description = stream.additional_metrics.get('video_details', {}).get('description', 'Sin descripción')
                        ui.label(description).classes('text-sm whitespace-pre-wrap')
                        
                        ui.label('Fecha de publicación:').classes('font-semibold')
                        published_at = stream.additional_metrics.get('video_details', {}).get('published_at', 'No disponible')
                        if published_at != 'No disponible':
                            try:
                                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                published_at = 'No disponible'
                        ui.label(published_at)
                        
                        ui.label('Categoría:').classes('font-semibold')
                        ui.label(stream.additional_metrics.get('video_details', {}).get('category_id', 'No disponible'))
                        
                        ui.label('Hora de inicio:').classes('font-semibold')
                        start_time = stream.additional_metrics.get('video_details', {}).get('start_time', 'No disponible')
                        if start_time != 'No disponible':
                            try:
                                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                start_time = 'No disponible'
                        ui.label(start_time)
                        
                        # Etiquetas
                        tags = stream.additional_metrics.get('video_details', {}).get('tags', [])
                        if tags:
                            ui.label('Etiquetas:').classes('font-semibold')
                            ui.label(', '.join(tags)).classes('text-sm')
                
                # Información del canal
                with ui.card().classes('w-full'):
                    ui.label('Información del Canal').classes('text-lg font-bold mb-2')
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        ui.label('ID del Canal:').classes('font-semibold')
                        ui.label(stream.additional_metrics.get('channel_details', {}).get('id', 'No disponible'))
                        
                        ui.label('Descripción:').classes('font-semibold')
                        channel_description = stream.additional_metrics.get('channel_details', {}).get('description', 'Sin descripción')
                        ui.label(channel_description).classes('text-sm whitespace-pre-wrap')
                        
                        ui.label('Fecha de creación:').classes('font-semibold')
                        channel_published = stream.additional_metrics.get('channel_details', {}).get('published_at', 'No disponible')
                        if channel_published != 'No disponible':
                            try:
                                channel_published = datetime.fromisoformat(channel_published.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                channel_published = 'No disponible'
                        ui.label(channel_published)
                        
                        ui.label('País:').classes('font-semibold')
                        ui.label(stream.additional_metrics.get('channel_details', {}).get('country', 'No disponible'))
                        
                        ui.label('Suscriptores:').classes('font-semibold')
                        ui.label(f"{stream.additional_metrics.get('channel_details', {}).get('subscriber_count', 0):,}")
                        
                        ui.label('Videos:').classes('font-semibold')
                        ui.label(f"{stream.additional_metrics.get('channel_details', {}).get('video_count', 0):,}")
                        
                        ui.label('Vistas totales:').classes('font-semibold')
                        ui.label(f"{stream.additional_metrics.get('channel_details', {}).get('view_count', 0):,}")
                        
                        ui.label('URL personalizada:').classes('font-semibold')
                        custom_url = stream.additional_metrics.get('channel_details', {}).get('custom_url', 'No disponible')
                        if custom_url != 'No disponible':
                            ui.link(custom_url, f"https://youtube.com/c/{custom_url}").classes('text-blue-500')
                        else:
                            ui.label(custom_url)
                        
                        # Palabras clave
                        keywords = stream.additional_metrics.get('channel_details', {}).get('keywords', '')
                        if keywords:
                            ui.label('Palabras clave:').classes('font-semibold')
                            ui.label(keywords).classes('text-sm')
                
                # Métricas actuales
                with ui.card().classes('w-full'):
                    ui.label('Métricas Actuales').classes('text-lg font-bold mb-2')
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        ui.label('Espectadores:').classes('font-semibold')
                        ui.label(f"{stream.current_viewers:,}")
                        ui.label('Likes:').classes('font-semibold')
                        ui.label(f"{stream.like_count:,}")
                        ui.label('Mensajes en vivo:').classes('font-semibold')
                        ui.label(f"{stream.live_chat_messages:,}")
                
                # Botón de cierre
                ui.button('Cerrar', on_click=dialog.close).classes('mt-4')
        
        dialog.open()

    def update_streams(self):
        """Actualiza los datos de los streams y los gráficos."""
        try:
            # Obtener datos actualizados
            streams = self.stream_service.get_all_streams()
            
            # Actualizar gráfico principal
            series = []
            x_data = []
            
            for stream in streams:
                if stream.viewer_history:
                    # Convertir timestamps a formato legible
                    x_data = [datetime.fromtimestamp(ts).strftime('%H:%M:%S') 
                             for ts, _ in stream.viewer_history]
                    
                    # Agregar serie para este stream
                    series.append({
                        'name': stream.title,
                        'type': 'line',
                        'data': [viewers for _, viewers in stream.viewer_history]
                    })
            
            self.main_chart.options['xAxis']['data'] = x_data
            self.main_chart.options['series'] = series
            self.main_chart.options['legend']['data'] = [s['name'] for s in series]
            self.main_chart.update()
            
            # Actualizar tarjetas de streams
            self.streams_container.clear()
            for stream in streams:
                with self.streams_container:
                    with ui.card().classes('w-full p-4'):
                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label(stream.title).classes('text-lg font-bold')
                            ui.label(f'{stream.current_viewers:,} viewers').classes('text-xl')
                        with ui.row().classes('w-full justify-between text-sm text-gray-500'):
                            ui.label(f'ID: {stream.video_id}')
                            ui.label(f'Última actualización: {datetime.fromtimestamp(stream.last_updated).strftime("%H:%M:%S")}')
            
        except Exception as e:
            logger.error(f"Error al actualizar streams: {str(e)}")

    def add_stream(self, video_id: str):
        """
        Agrega un nuevo stream a la aplicación.
        
        Args:
            video_id (str): ID del video de YouTube a monitorear
        """
        try:
            if not video_id:
                ui.notify('Por favor ingrese un ID de video válido', type='negative')
                return
                
            # Intentar agregar el stream
            stream = self.stream_service.add_stream(video_id)
            if stream:
                ui.notify(f'Stream agregado: {stream.title}', type='positive')
                # Actualizar la interfaz
                self.update_streams()
            else:
                ui.notify('No se pudo agregar el stream. Verifique el ID del video.', type='negative')
                
        except Exception as e:
            logger.error(f"Error al agregar stream: {str(e)}")
            ui.notify('Error al agregar el stream', type='negative')

if __name__ in {"__main__", "__mp_main__"}:
    app = StreamViewerApp()
    app.start() 