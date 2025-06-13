import os
from pathlib import Path
from dotenv import load_dotenv # type: ignore
from .logger import logger

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Config:
    """
    Clase de configuración para la aplicación Stream Views.
    
    Maneja la carga y validación de variables de entorno y configuración.
    """
    
    # Configuración de la API de YouTube
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///stream_views.db')
    
    # Configuración de seguridad
    MAX_REQUESTS_PER_HOUR = int(os.getenv('MAX_REQUESTS_PER_HOUR', '100'))
    API_RATE_LIMIT_WINDOW = int(os.getenv('API_RATE_LIMIT_WINDOW', '3600'))
    ENABLE_CSRF_PROTECTION = os.getenv('ENABLE_CSRF_PROTECTION', 'true').lower() == 'true'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/stream_views.log')
    MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', '10485760'))  # 10MB
    MAX_LOG_FILES = int(os.getenv('MAX_LOG_FILES', '5'))
    
    # Configuración de la aplicación
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '30'))
    MAX_STREAMS = int(os.getenv('MAX_STREAMS', '50'))
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida la configuración de la aplicación.
        
        Returns:
            bool: True si la configuración es válida, False en caso contrario
        """
        try:
            # Validar API key
            if not cls.YOUTUBE_API_KEY:
                logger.error("No se encontró la clave API de YouTube")
                return False
            
            # Verificar longitud y formato de la API key
            if len(cls.YOUTUBE_API_KEY) != 39 or not cls.YOUTUBE_API_KEY.startswith('AIza'):
                logger.error("La clave API de YouTube no tiene el formato correcto")
                return False
            
            logger.info("API key de YouTube validada correctamente")
            
            # Validar directorio de logs
            log_dir = Path(cls.LOG_FILE_PATH).parent
            log_dir.mkdir(exist_ok=True)
            
            # Validar configuración de seguridad
            if cls.MAX_REQUESTS_PER_HOUR <= 0:
                logger.error("MAX_REQUESTS_PER_HOUR debe ser mayor que 0")
                return False
            
            if cls.API_RATE_LIMIT_WINDOW <= 0:
                logger.error("API_RATE_LIMIT_WINDOW debe ser mayor que 0")
                return False
            
            # Validar configuración de la aplicación
            if cls.UPDATE_INTERVAL <= 0:
                logger.error("UPDATE_INTERVAL debe ser mayor que 0")
                return False
            
            if cls.MAX_STREAMS <= 0:
                logger.error("MAX_STREAMS debe ser mayor que 0")
                return False
            
            logger.info("Configuración validada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al validar la configuración: {str(e)}")
            return False
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Obtiene la URL de la base de datos.
        
        Returns:
            str: URL de la base de datos
        """
        return cls.DATABASE_URL
    
    @classmethod
    def get_log_config(cls) -> dict:
        """
        Obtiene la configuración de logging.
        
        Returns:
            dict: Configuración de logging
        """
        return {
            'level': cls.LOG_LEVEL,
            'file_path': cls.LOG_FILE_PATH,
            'max_size': cls.MAX_LOG_SIZE,
            'max_files': cls.MAX_LOG_FILES
        }
    
    @classmethod
    def get_security_config(cls) -> dict:
        """
        Obtiene la configuración de seguridad.
        
        Returns:
            dict: Configuración de seguridad
        """
        return {
            'max_requests': cls.MAX_REQUESTS_PER_HOUR,
            'time_window': cls.API_RATE_LIMIT_WINDOW,
            'enable_csrf': cls.ENABLE_CSRF_PROTECTION
        }

# Instancia global de configuración
config = Config() 