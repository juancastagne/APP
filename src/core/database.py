from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from .config import Config
from .logger import logger

# Obtener la ruta de la base de datos
db_path = Config.DATABASE_URL.replace('sqlite:///', '')

# Crear el motor de la base de datos
engine = create_engine(Config.DATABASE_URL)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

def get_db():
    """
    Obtiene una sesión de base de datos.
    
    Returns:
        Session: Sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    try:
        # Si la base de datos existe, eliminarla
        if os.path.exists(db_path):
            logger.info(f"Eliminando base de datos existente: {db_path}")
            os.remove(db_path)
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise 