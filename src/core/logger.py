import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

class StreamLogger:
    """
    Sistema de logging personalizado para la aplicación Stream Views.
    
    Este logger maneja tanto la salida a consola como a archivo, con rotación
    automática de logs y diferentes niveles de logging.
    """
    
    def __init__(self, name="stream_views"):
        """
        Inicializa el sistema de logging.
        
        Args:
            name (str): Nombre del logger
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Formato para los logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler para archivo con rotación
        file_handler = RotatingFileHandler(
            log_dir / f"stream_views_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Agregar handlers al logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Registra un mensaje de nivel DEBUG."""
        self.logger.debug(message)
    
    def info(self, message):
        """Registra un mensaje de nivel INFO."""
        self.logger.info(message)
    
    def warning(self, message):
        """Registra un mensaje de nivel WARNING."""
        self.logger.warning(message)
    
    def error(self, message):
        """Registra un mensaje de nivel ERROR."""
        self.logger.error(message)
    
    def critical(self, message):
        """Registra un mensaje de nivel CRITICAL."""
        self.logger.critical(message)

# Instancia global del logger
logger = StreamLogger() 