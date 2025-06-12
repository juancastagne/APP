from dotenv import load_dotenv
import os
from pathlib import Path
import logging

# Cargar variables de entorno desde el directorio raíz
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from src.ui.app import StreamViewerApp

logger = logging.getLogger(__name__)

if __name__ in {"__main__", "__mp_main__"}:
    try:
        app = StreamViewerApp()
        app.start()
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise 