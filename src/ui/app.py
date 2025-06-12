from nicegui import ui # type: ignore
from src.services.stream_service import StreamService
from src.core.logger import logger
from src.core.monitoring import system_monitor
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
        metrics_chart: Gráfico para visualizar métricas del sistema
    """

    def __init__(self):
        """
        Inicializa la aplicación con los servicios necesarios y estructuras de datos.
        """
        logger.info("Iniciando aplicación Stream Views")
        self.stream_service = StreamService()
        self.stream_cards = {}
        self.historical_data = defaultdict(list)
        self.main_chart = None
        self.metrics_chart = None
        logger.debug("Aplicación inicializada correctamente")

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

    def update_chart(self):
        """
        Actualiza el gráfico principal con los datos históricos de todos los streams.
        El gráfico muestra la evolución de visualizadores a lo largo del tiempo.
        """
        if not self.main_chart:
            return

        # Configuración inicial del gráfico
        chart_options = {
            'title': {
                'text': 'Evolución de Visualizadores',
                'left': 'center'
            },
            'tooltip': {
                'trigger': 'axis'
            },
            'legend': {
                'data': [],
                'bottom': 0
            },
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
                'nameLocation': 'middle',
                'nameGap': 40
            },
            'series': []
        }

        # Preparar datos para el gráfico
        all_times = set()
        all_data = {}
        
        # Primero recolectamos todos los tiempos y datos
        for stream_id, data in self.historical_data.items():
            if data:
                stream = self.stream_service.get_stream_details(stream_id)
                if stream:
                    # Redondeamos los timestamps al segundo más cercano para mejor alineación
                    all_data[stream.title] = {
                        datetime(
                            t.year, t.month, t.day, 
                            t.hour, t.minute, t.second
                        ): d['viewers'] 
                        for t, d in zip(
                            [d['timestamp'] for d in data],
                            data
                        )
                    }
                    all_times.update(all_data[stream.title].keys())

        if all_times:
            # Ordenar tiempos y convertirlos a formato HH:MM:SS
            sorted_times = sorted(all_times)
            x_data = [t.strftime('%H:%M:%S') for t in sorted_times]
            chart_options['xAxis']['data'] = x_data

            # Preparar series
            colors = ['#2196F3', '#4CAF50', '#FFC107', '#9C27B0', '#FF5722']
            for i, (stream_name, data) in enumerate(all_data.items()):
                chart_options['legend']['data'].append(stream_name)
                chart_options['series'].append({
                    'name': stream_name,
                    'type': 'line',
                    'data': [data.get(t, None) for t in sorted_times],
                    'connectNulls': True,
                    'smooth': True,
                    'lineStyle': {
                        'width': 2,
                        'color': colors[i % len(colors)]
                    },
                    'areaStyle': {
                        'color': colors[i % len(colors)],
                        'opacity': 0.1
                    },
                    'symbol': 'circle',
                    'symbolSize': 6
                })

        self.main_chart.options.update(chart_options)
        self.main_chart.update()

    def update_metrics_chart(self):
        """
        Actualiza el gráfico de métricas del sistema.
        """
        if not self.metrics_chart:
            return

        metrics = system_monitor.collect_metrics()
        if not metrics:
            return

        chart_options = {
            'title': {
                'text': 'Métricas del Sistema',
                'left': 'center'
            },
            'tooltip': {
                'trigger': 'axis'
            },
            'legend': {
                'data': ['CPU', 'Memoria', 'Llamadas API', 'Actualizaciones', 'Errores'],
                'bottom': 0
            },
            'xAxis': {
                'type': 'category',
                'data': [m['timestamp'].strftime('%H:%M:%S') for m in system_monitor.metrics_history['cpu_percent']],
                'name': 'Hora',
                'nameLocation': 'middle',
                'nameGap': 30
            },
            'yAxis': [
                {
                    'type': 'value',
                    'name': 'Porcentaje',
                    'min': 0,
                    'max': 100,
                    'position': 'left'
                },
                {
                    'type': 'value',
                    'name': 'Cantidad',
                    'position': 'right'
                }
            ],
            'series': [
                {
                    'name': 'CPU',
                    'type': 'line',
                    'data': list(system_monitor.metrics_history['cpu_percent']),
                    'yAxisIndex': 0
                },
                {
                    'name': 'Memoria',
                    'type': 'line',
                    'data': list(system_monitor.metrics_history['memory_percent']),
                    'yAxisIndex': 0
                },
                {
                    'name': 'Llamadas API',
                    'type': 'line',
                    'data': list(system_monitor.metrics_history['api_calls']),
                    'yAxisIndex': 1
                },
                {
                    'name': 'Actualizaciones',
                    'type': 'line',
                    'data': list(system_monitor.metrics_history['stream_updates']),
                    'yAxisIndex': 1
                },
                {
                    'name': 'Errores',
                    'type': 'line',
                    'data': list(system_monitor.metrics_history['errors']),
                    'yAxisIndex': 1
                }
            ]
        }

        self.metrics_chart.options.update(chart_options)
        self.metrics_chart.update()

    def update_streams(self):
        """
        Actualiza los datos de todos los streams monitoreados.
        Este método se ejecuta periódicamente para mantener la información actualizada.
        """
        logger.debug("Iniciando actualización de streams")
        try:
            for stream in self.stream_service.get_all_streams():
                system_monitor.increment_api_calls()
                updated_stream = self.stream_service.update_stream_metrics(stream.video_id)
                if updated_stream:
                    system_monitor.increment_stream_updates()
                    # Actualizar datos históricos
                    current_time = datetime.now()
                    self.historical_data[updated_stream.video_id].append({
                        'timestamp': current_time,
                        'viewers': updated_stream.current_viewers
                    })
                    # Actualizar tarjeta
                    if updated_stream.video_id in self.stream_cards:
                        self.stream_cards[updated_stream.video_id].delete()
                    self.create_stream_card(updated_stream)
            
            # Actualizar gráficos
            self.update_chart()
            self.update_metrics_chart()
            logger.debug("Actualización de streams completada")
        except Exception as e:
            system_monitor.increment_errors()
            logger.error(f"Error al actualizar streams: {str(e)}")

    def start(self):
        """
        Inicia la aplicación y configura la interfaz de usuario principal.
        Este método debe ser llamado para comenzar la ejecución de la aplicación.
        """
        logger.info("Iniciando interfaz de usuario")
        try:
            # Contenedor principal
            with ui.column().classes('w-full h-full p-4 gap-4'):
                # Título
                ui.label('Monitor de Streams de YouTube').classes('text-2xl font-bold mb-4')
                
                # Formulario para agregar stream
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('w-full items-center gap-4'):
                        video_id_input = ui.input(
                            label='ID del Video',
                            placeholder='Ingrese el ID del video de YouTube'
                        ).classes('flex-grow')
                        ui.button(
                            'Agregar Stream',
                            on_click=lambda: self.add_stream(video_id_input.value)
                        ).classes('bg-blue-500 text-white')
                
                # Gráfico de métricas del sistema
                self.metrics_chart = ui.echart({
                    'title': {'text': 'Métricas del Sistema'},
                    'tooltip': {'trigger': 'axis'},
                    'legend': {'data': [], 'bottom': 0},
                    'xAxis': {
                        'type': 'category',
                        'data': [],
                        'name': 'Hora',
                        'nameLocation': 'middle',
                        'nameGap': 30
                    },
                    'yAxis': [
                        {
                            'type': 'value',
                            'name': 'Porcentaje',
                            'min': 0,
                            'max': 100,
                            'position': 'left'
                        },
                        {
                            'type': 'value',
                            'name': 'Cantidad',
                            'position': 'right'
                        }
                    ],
                    'series': []
                }).classes('w-full h-48')
                
                # Gráfico principal de streams
                self.main_chart = ui.echart({
                    'title': {'text': 'Evolución de Visualizadores'},
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
                        'nameLocation': 'middle',
                        'nameGap': 40
                    },
                    'series': []
                }).classes('w-full h-96')
                
                # Contenedor de tarjetas
                with ui.column().classes('w-full gap-4'):
                    for stream in self.stream_service.get_all_streams():
                        self.create_stream_card(stream)
            
            # Iniciar actualización periódica
            ui.timer(30.0, self.update_streams)
            logger.info("Interfaz de usuario iniciada correctamente")
        except Exception as e:
            system_monitor.increment_errors()
            logger.error(f"Error al iniciar la interfaz: {str(e)}")

    def add_stream(self, video_id):
        """
        Agrega un nuevo stream para monitorear.
        
        Args:
            video_id (str): ID del video de YouTube a monitorear
            
        Returns:
            bool: True si el stream se agregó exitosamente, False en caso contrario
        """
        if not video_id:
            ui.notify('Por favor ingrese un ID de video válido', type='negative')
            return False
        
        try:
            stream = self.stream_service.add_stream(video_id)
            if stream:
                self.create_stream_card(stream)
                ui.notify('Stream agregado exitosamente', type='positive')
                return True
            else:
                ui.notify('No se pudo agregar el stream', type='negative')
                return False
        except Exception as e:
            system_monitor.increment_errors()
            logger.error(f"Error al agregar stream: {str(e)}")
            ui.notify(f'Error al agregar stream: {str(e)}', type='negative')
            return False

if __name__ in {"__main__", "__mp_main__"}:
    app = StreamViewerApp()
    app.start() 