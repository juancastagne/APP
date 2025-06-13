from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base

class Stream(Base):
    """
    Modelo para representar un stream de YouTube.
    """
    __tablename__ = 'streams'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False, default='Sin título')
    channel_name = Column(String(100), nullable=False, default='Sin canal')
    thumbnail_url = Column(String(200), nullable=False, default='')
    current_viewers = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con las métricas
    metrics = relationship("StreamMetrics", back_populates="stream", cascade="all, delete-orphan")
    
    def __init__(self, video_id: str, title: str = None, channel_name: str = None, 
                 thumbnail_url: str = None, current_viewers: int = 0, is_active: bool = True):
        self.video_id = video_id
        self.title = title or 'Sin título'
        self.channel_name = channel_name or 'Sin canal'
        self.thumbnail_url = thumbnail_url or ''
        self.current_viewers = current_viewers
        self.is_active = is_active
        self.last_updated = datetime.utcnow()
        self.created_at = datetime.utcnow()

class StreamMetrics(Base):
    """
    Modelo para almacenar las métricas de un stream.
    """
    __tablename__ = 'stream_metrics'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), ForeignKey('streams.video_id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    current_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    live_chat_messages = Column(Integer, default=0)
    subscriber_count = Column(Integer, default=0)
    additional_metrics = Column(JSON, default=dict)
    
    # Relación con el stream
    stream = relationship("Stream", back_populates="metrics")
    
    def __init__(self, video_id: str, current_viewers: int = 0, total_views: int = 0,
                 like_count: int = 0, comment_count: int = 0, live_chat_messages: int = 0,
                 subscriber_count: int = 0, additional_metrics: dict = None):
        self.video_id = video_id
        self.timestamp = datetime.utcnow()
        self.current_viewers = current_viewers
        self.total_views = total_views
        self.like_count = like_count
        self.comment_count = comment_count
        self.live_chat_messages = live_chat_messages
        self.subscriber_count = subscriber_count
        self.additional_metrics = additional_metrics or {} 