from dotenv import load_dotenv
import os
from pathlib import Path

# Cargar variables de entorno desde el directorio raíz
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from src.ui.app import StreamViewerApp

if __name__ in {"__main__", "__mp_main__"}:
    app = StreamViewerApp()
    app.start() 