from datetime import datetime
from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field, GetJsonSchemaHandler, BeforeValidator
from bson import ObjectId

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return ObjectId(v)

class StreamMetrics(BaseModel):
    """Modelo para las métricas de un stream."""
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    stream_id: str
    concurrent_viewers: int
    total_views: int
    like_count: int
    comment_count: int
    live_chat_messages: int
    subscriber_count: int
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

class Stream(BaseModel):
    """Modelo para un stream de YouTube."""
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    video_id: str
    title: str
    channel_name: str
    thumbnail_url: Optional[str] = None
    current_viewers: int = 0
    is_active: bool = True
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    } 