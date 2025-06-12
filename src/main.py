import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from nicegui import ui

# Cargar variables de entorno desde el directorio raíz
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from src.ui.app import StreamViewerApp

logger = logging.getLogger(__name__)

def main():
    try:
        # Inicializar la aplicación
        app = StreamViewerApp()
        
        # Obtener el puerto de la variable de entorno o usar 8080 por defecto
        port = int(os.getenv('PORT', 8080))
        
        # Iniciar el servidor
        ui.run(port=port, host='0.0.0.0')
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise

if __name__ == "__main__":
    main() 