from typing import Dict, List
import plotly.graph_objects as go
from nicegui import ui
from datetime import datetime, timedelta
import pandas as pd
from src.services.stream_service import StreamService

class StreamGraph:
    def __init__(self):
        self.data: Dict[str, List[Dict]] = {}
        self.fig = go.Figure()
        self.plot = None  # Inicializamos como None
        self.stream_service = StreamService()
        
        # Configuración inicial del gráfico
        self.fig.update_layout(
            title='Evolución de Viewers en Tiempo Real',
            xaxis_title='Tiempo',
            yaxis_title='Viewers',
            showlegend=True,
            template='plotly_dark'
        )
        
    def setup(self):
        """Configura el gráfico en la interfaz."""
        self.plot = ui.plotly(self.fig).classes('w-full h-96')
        
    def update_data(self, stream_id: str, viewers: int, timestamp: datetime):
        """Actualiza los datos del gráfico con nuevos valores."""
        if stream_id not in self.data:
            self.data[stream_id] = []
            
        self.data[stream_id].append({
            'timestamp': timestamp,
            'viewers': viewers
        })
        
        # Mantener solo los últimos 30 minutos de datos
        cutoff_time = datetime.now() - timedelta(minutes=30)
        self.data[stream_id] = [
            point for point in self.data[stream_id]
            if point['timestamp'] > cutoff_time
        ]
        
        self._update_plot()
        
    def _update_plot(self):
        """Actualiza el gráfico con los datos más recientes."""
        if self.plot is None:
            return
            
        self.fig.data = []  # Limpiar datos existentes
        
        for stream_id, points in self.data.items():
            df = pd.DataFrame(points)
            # Obtener el stream para acceder al nombre del canal
            stream = self.stream_service.get_stream_details(stream_id)
            channel_name = stream.channel_name if stream else stream_id
            
            self.fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['viewers'],
                    name=channel_name,
                    mode='lines+markers'
                )
            )
            
        # Actualizar el rango del eje X para mostrar solo los últimos 30 minutos
        now = datetime.now()
        self.fig.update_xaxes(
            range=[now - timedelta(minutes=30), now],
            autorange=False
        )
        
        # Actualizar el rango del eje Y para que se ajuste automáticamente
        self.fig.update_yaxes(autorange=True)
        
        self.plot.update() 