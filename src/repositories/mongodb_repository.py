from typing import List, Optional
from datetime import datetime
from ..core.database import Database
from ..models.mongodb_models import Stream, Channel, ViewerHistory

class MongoDBRepository:
    def __init__(self):
        self.db = Database.get_database()

    # Stream Operations
    async def create_stream(self, stream: Stream) -> Stream:
        stream_dict = stream.model_dump(by_alias=True)
        result = await self.db.streams.insert_one(stream_dict)
        stream_dict["_id"] = result.inserted_id
        return Stream(**stream_dict)

    async def get_stream(self, stream_id: str) -> Optional[Stream]:
        stream = await self.db.streams.find_one({"stream_id": stream_id})
        return Stream(**stream) if stream else None

    async def get_active_streams(self) -> List[Stream]:
        cursor = self.db.streams.find({"timestamp": {"$gte": datetime.utcnow()}})
        return [Stream(**doc) async for doc in cursor]

    # Channel Operations
    async def create_channel(self, channel: Channel) -> Channel:
        channel_dict = channel.model_dump(by_alias=True)
        result = await self.db.channels.insert_one(channel_dict)
        channel_dict["_id"] = result.inserted_id
        return Channel(**channel_dict)

    async def get_channel(self, channel_id: str) -> Optional[Channel]:
        channel = await self.db.channels.find_one({"channel_id": channel_id})
        return Channel(**channel) if channel else None

    async def update_channel(self, channel_id: str, update_data: dict) -> Optional[Channel]:
        result = await self.db.channels.find_one_and_update(
            {"channel_id": channel_id},
            {"$set": update_data},
            return_document=True
        )
        return Channel(**result) if result else None

    # Viewer History Operations
    async def add_viewer_history(self, history: ViewerHistory) -> ViewerHistory:
        history_dict = history.model_dump(by_alias=True)
        result = await self.db.viewer_history.insert_one(history_dict)
        history_dict["_id"] = result.inserted_id
        return ViewerHistory(**history_dict)

    async def get_stream_history(self, stream_id: str, limit: int = 100) -> List[ViewerHistory]:
        cursor = self.db.viewer_history.find(
            {"stream_id": stream_id}
        ).sort("timestamp", -1).limit(limit)
        return [ViewerHistory(**doc) async for doc in cursor]

    async def get_channel_history(self, channel_id: str, limit: int = 100) -> List[ViewerHistory]:
        cursor = self.db.viewer_history.find(
            {"channel_id": channel_id}
        ).sort("timestamp", -1).limit(limit)
        return [ViewerHistory(**doc) async for doc in cursor] 