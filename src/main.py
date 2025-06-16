import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
from nicegui import ui
from .core.config import Config
from .core.database import init_db
from .core.logger import logger
from .ui.app import StreamViewerApp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import auth_routes
from src.services.data_processor import DataProcessor
import uvicorn

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
        init_db()
        logger.info("Base de datos inicializada correctamente")
        
        # Crear la aplicación
        app = StreamViewerApp()
        logger.info("Aplicación creada correctamente")
        
        # Iniciar la aplicación
        app.start()
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        raise

# Ejecutar main() directamente
main()

app = FastAPI(title="Stream Views API")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth_routes.router)

# Inicializar servicios
data_processor = DataProcessor()

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    # Aquí puedes agregar código de inicialización
    pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 