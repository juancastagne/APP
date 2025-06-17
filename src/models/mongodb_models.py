from pydantic import BaseModel, Field, GetJsonSchemaHandler
from datetime import datetime
from typing import Optional, List, Any, Annotated
from bson import ObjectId # type: ignore

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
    def __get_pydantic_json_schema__(cls, _schema_generator: GetJsonSchemaHandler) -> dict[str, Any]:
        return {"type": "string"}

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> dict[str, Any]:
        return {
            "type": "string",
            "description": "ObjectId",
            "custom_validator": lambda x: cls.validate(x)
        }

class StreamBase(BaseModel):
    channel_id: str
    channel_name: str
    stream_id: str
    title: str
    viewer_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_live: bool = True
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    }

class Stream(StreamBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]

class ChannelBase(BaseModel):
    channel_id: str
    channel_name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    view_count: Optional[int] = None
    video_count: Optional[int] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    }

class Channel(ChannelBase):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]

class ViewerHistory(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    stream_id: str
    channel_id: str
    viewer_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period_type: str = "raw"  # raw, 5min_average, daily_average

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    }

class User(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    email: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    favorite_streams: List[str] = []  # Lista de stream_ids
    notification_preferences: dict = Field(default_factory=dict)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    }

class StreamAnalytics(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    stream_id: str
    channel_id: str
    period_start: datetime
    period_end: datetime
    average_viewers: float
    peak_viewers: int
    total_duration: int  # en segundos
    period_type: str  # 5min, daily, weekly, monthly

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    } 