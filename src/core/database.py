from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from pymongo import MongoClient # type: ignore
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """Conecta a la base de datos MongoDB."""
        if cls.client is None:
            mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            cls.client = AsyncIOMotorClient(mongo_url)
            cls.db = cls.client.stream_views
            logger.info("Conectado a MongoDB!")

    @classmethod
    async def close_database_connection(cls):
        """Cierra la conexión a la base de datos."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            logger.info("Conexión a MongoDB cerrada!")

    @classmethod
    def get_database(cls):
        """Retorna la instancia de la base de datos."""
        return cls.db

# Obtener la URL de MongoDB desde las variables de entorno
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')

# Cliente síncrono para operaciones que no requieren async
client = MongoClient(MONGODB_URL)
db = client.stream_views

# Cliente asíncrono para operaciones que requieren async
async_client = AsyncIOMotorClient(MONGODB_URL)
async_db = async_client.stream_views

def get_db():
    """Obtiene la instancia de la base de datos."""
    try:
        yield db
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {str(e)}")
        raise

async def get_async_db():
    """Obtiene la instancia asíncrona de la base de datos."""
    try:
        yield async_db
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos asíncrona: {str(e)}")
        raise 