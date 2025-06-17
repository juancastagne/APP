import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
from nicegui import ui
from .core.config import Config
from .core.database import Database
from .core.logger import logger
from .ui.app import StreamViewerApp

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Cargar variables de entorno
env_path = root_dir.parent / '.env'
load_dotenv(env_path)

def main():
    """
    Función principal que inicia la aplicación.
    """
    try:
        # Validar la configuración
        if not Config.validate():
            logger.error("Error en la configuración de la aplicación")
            return
        
        # Inicializar la base de datos
        Database.connect_to_database()
        logger.info("Base de datos inicializada correctamente")
        
        # Crear la aplicación
        app = StreamViewerApp()
        logger.info("Aplicación creada correctamente")
        
        # Iniciar la aplicación
        app.start()
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise
    finally:
        # Cerrar la conexión a la base de datos
        Database.close_database_connection()

# Ejecutar main() directamente
if __name__ == "__main__":
    main() 