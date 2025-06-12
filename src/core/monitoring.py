import psutil # type: ignore
import time
from datetime import datetime
from collections import deque
from .logger import logger

class SystemMonitor:
    """
    Monitoreo del sistema y métricas de la aplicación.
    
    Esta clase recolecta y almacena métricas del sistema como uso de CPU,
    memoria, y métricas específicas de la aplicación.
    """
    
    def __init__(self, history_size=100):
        """
        Inicializa el monitor del sistema.
        
        Args:
            history_size (int): Tamaño del historial de métricas
        """
        self.history_size = history_size
        self.metrics_history = {
            'cpu_percent': deque(maxlen=history_size),
            'memory_percent': deque(maxlen=history_size),
            'api_calls': deque(maxlen=history_size),
            'stream_updates': deque(maxlen=history_size),
            'errors': deque(maxlen=history_size)
        }
        self.start_time = time.time()
        self.api_calls_count = 0
        self.stream_updates_count = 0
        self.error_count = 0
    
    def collect_metrics(self):
        """
        Recolecta métricas actuales del sistema.
        
        Returns:
            dict: Diccionario con las métricas actuales
        """
        try:
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'api_calls': self.api_calls_count,
                'stream_updates': self.stream_updates_count,
                'errors': self.error_count,
                'uptime': time.time() - self.start_time
            }
            
            # Actualizar historial
            for key, value in metrics.items():
                if key in self.metrics_history:
                    self.metrics_history[key].append(value)
            
            return metrics
        except Exception as e:
            logger.error(f"Error al recolectar métricas: {str(e)}")
            return None
    
    def increment_api_calls(self):
        """Incrementa el contador de llamadas a la API."""
        self.api_calls_count += 1
    
    def increment_stream_updates(self):
        """Incrementa el contador de actualizaciones de streams."""
        self.stream_updates_count += 1
    
    def increment_errors(self):
        """Incrementa el contador de errores."""
        self.error_count += 1
    
    def get_metrics_summary(self):
        """
        Obtiene un resumen de las métricas actuales.
        
        Returns:
            dict: Resumen de métricas
        """
        return {
            'uptime': time.time() - self.start_time,
            'total_api_calls': self.api_calls_count,
            'total_stream_updates': self.stream_updates_count,
            'total_errors': self.error_count,
            'current_cpu': psutil.cpu_percent(),
            'current_memory': psutil.virtual_memory().percent
        }

# Instancia global del monitor
system_monitor = SystemMonitor() 