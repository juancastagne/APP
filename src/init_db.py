import logging
from pathlib import Path
from repositories.database import Database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa la base de datos y crea las tablas necesarias"""
    try:
        # Obtener la ruta del directorio del proyecto
        project_root = Path(__file__).parent.parent
        db_path = project_root / "stream_views.db"
        
        logger.info(f"Inicializando base de datos en: {db_path}")
        
        # Crear instancia de Database (esto creará las tablas si no existen)
        with Database(str(db_path)) as db:
            logger.info("Base de datos inicializada correctamente")
            
            # Verificar que las tablas existan
            db.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = db.cursor.fetchall()
            
            logger.info("Tablas existentes:")
            for table in tables:
                logger.info(f"- {table[0]}")
                
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 