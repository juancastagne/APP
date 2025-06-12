import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "stream_views.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_database()

    def _initialize_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        try:
            # Asegurarse de que el directorio existe
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Crear tabla streams
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS streams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    channel_id TEXT,
                    channel_title TEXT,
                    thumbnail_url TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    scheduled_start DATETIME,
                    scheduled_end DATETIME,
                    status TEXT,
                    privacy TEXT,
                    license TEXT,
                    embeddable BOOLEAN,
                    public_stats_viewable BOOLEAN,
                    made_for_kids BOOLEAN,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear tabla stream_metrics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stream_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_id INTEGER NOT NULL,
                    current_viewers INTEGER,
                    total_views INTEGER,
                    like_count INTEGER,
                    comment_count INTEGER,
                    live_chat_messages INTEGER,
                    subscriber_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stream_id) REFERENCES streams(id)
                )
            """)

            # Crear tabla channel_metrics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    subscriber_count INTEGER,
                    video_count INTEGER,
                    view_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear tabla topics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear tabla stream_topics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stream_topics (
                    stream_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    confidence FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (stream_id, topic_id),
                    FOREIGN KEY (stream_id) REFERENCES streams(id),
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                )
            """)

            # Crear tabla topic_metrics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    total_streams INTEGER,
                    total_viewers INTEGER,
                    avg_viewers FLOAT,
                    max_viewers INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
                )
            """)

            self.conn.commit()

            # Crear índices después de crear las tablas
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_streams_video_id ON streams(video_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_streams_session_id ON streams(session_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_stream_metrics_stream_id ON stream_metrics(stream_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_stream_metrics_timestamp ON stream_metrics(timestamp)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_metrics_channel_id ON channel_metrics(channel_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_metrics_timestamp ON channel_metrics(timestamp)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_stream_topics_stream_id ON stream_topics(stream_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_stream_topics_topic_id ON stream_topics(topic_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic_metrics_topic_id ON topic_metrics(topic_id)")

            self.conn.commit()
            logger.info("Base de datos inicializada correctamente")

        except sqlite3.Error as e:
            logger.error(f"Error al inicializar la base de datos: {str(e)}")
            raise

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión a la base de datos cerrada")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 