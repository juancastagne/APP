from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from typing import Optional
import os
from dotenv import load_dotenv
from ..core.logger import logger
import certifi
import ssl

# Cargar variables de entorno
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """Conecta a la base de datos MongoDB."""
        try:
            if cls.client is None:
                # Usar la URL de MongoDB Atlas desde las variables de entorno
                mongo_url = os.getenv("MONGODB_URI")
                if not mongo_url:
                    raise ValueError("MONGODB_URI no está configurada en las variables de entorno")
                
                # Configurar el cliente con SSL y certificados
                cls.client = AsyncIOMotorClient(
                    mongo_url,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=30000,
                    tlsAllowInvalidCertificates=True,  # Permitir certificados inválidos temporalmente
                    ssl=True,
                    retryWrites=True,
                    w='majority'
                )
                
                # Verificar la conexión
                await cls.client.admin.command('ping')
                cls.db = cls.client.stream_views
                logger.info("Conectado a MongoDB Atlas!")
        except Exception as e:
            logger.error(f"Error al conectar con MongoDB: {str(e)}")
            raise

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
        if cls.db is None:
            raise RuntimeError("La base de datos no está inicializada. Llame a connect_to_database primero.")
        return cls.db

# Obtener la URL de MongoDB desde las variables de entorno
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')

async def get_db():
    """Obtiene la instancia de la base de datos."""
    try:
        if Database.db is None:
            await Database.connect_to_database()
        return Database.db
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {str(e)}")
        raise 