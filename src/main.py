import os
import sys
import asyncio
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

async def init_database():
    """Inicializa la conexión a la base de datos."""
    await Database.connect_to_database()
    logger.info("Base de datos inicializada correctamente")

async def close_database():
    """Cierra la conexión a la base de datos."""
    await Database.close_database_connection()
    logger.info("Conexión a la base de datos cerrada")

def main():
    """
    Función principal que inicia la aplicación.
    """
    try:
        # Validar la configuración
        if not Config.validate():
            logger.error("Error en la configuración de la aplicación")
            return
        
        # Inicializar la base de datos de forma asíncrona
        asyncio.run(init_database())
        
        # Crear la aplicación
        app = StreamViewerApp()
        logger.info("Aplicación creada correctamente")
        
        # Iniciar la aplicación
        app.start()
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise
    finally:
        # Cerrar la conexión a la base de datos de forma asíncrona
        asyncio.run(close_database())

# Ejecutar main() directamente
if __name__ == "__main__":
    main() 