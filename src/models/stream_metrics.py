from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class StreamMetrics(BaseModel):
    """Modelo para las métricas de un stream."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    stream_id: str
    concurrent_viewers: int
    total_views: int
    like_count: int
    comment_count: int
    live_chat_messages: int
    subscriber_count: int
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

class Stream(BaseModel):
    """Modelo para un stream de YouTube."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    video_id: str
    title: str
    channel_name: str
    thumbnail_url: Optional[str] = None
    current_viewers: int = 0
    is_active: bool = True
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True 