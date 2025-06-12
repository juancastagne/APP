from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class StreamMetrics:
    video_id: str
    title: str
    channel_title: str
    thumbnail_url: str
    current_viewers: int
    total_views: int
    like_count: int
    comment_count: int
    live_chat_messages: int
    subscriber_count: int
    additional_metrics: Dict[str, any]
    metrics_history: List[Dict[str, any]]
    last_updated: datetime

    def __init__(self, video_id: str, title: str, channel_title: str, thumbnail_url: str,
                 current_viewers: int, total_views: int, like_count: int, comment_count: int,
                 live_chat_messages: int, subscriber_count: int, additional_metrics: Optional[Dict[str, any]] = None):
        self.video_id = video_id
        self.title = title
        self.channel_title = channel_title
        self.thumbnail_url = thumbnail_url
        self.current_viewers = current_viewers
        self.total_views = total_views
        self.like_count = like_count
        self.comment_count = comment_count
        self.live_chat_messages = live_chat_messages
        self.subscriber_count = subscriber_count
        self.metrics_history = []
        self.last_updated = datetime.now()
        # Asegurarnos de que additional_metrics contiene video_details y channel_details
        self.additional_metrics = {
            'video_details': additional_metrics.get('video_details', {}),
            'channel_details': additional_metrics.get('channel_details', {}),
            'start_time': additional_metrics.get('start_time'),
            'end_time': additional_metrics.get('end_time'),
            'scheduled_start': additional_metrics.get('scheduled_start'),
            'scheduled_end': additional_metrics.get('scheduled_end'),
            'chat_id': additional_metrics.get('chat_id'),
            'duration': additional_metrics.get('duration'),
            'status': additional_metrics.get('status'),
            'privacy': additional_metrics.get('privacy'),
            'license': additional_metrics.get('license'),
            'embeddable': additional_metrics.get('embeddable'),
            'public_stats_viewable': additional_metrics.get('public_stats_viewable'),
            'made_for_kids': additional_metrics.get('made_for_kids'),
            'topics': additional_metrics.get('topics', [])
        } if additional_metrics else {}

    def update_metrics(self, current_viewers: int, total_views: int, like_count: int, comment_count: int,
                      live_chat_messages: int, subscriber_count: int, additional_metrics: Optional[Dict[str, any]] = None):
        self.current_viewers = current_viewers
        self.total_views = total_views
        self.like_count = like_count
        self.comment_count = comment_count
        self.live_chat_messages = live_chat_messages
        self.subscriber_count = subscriber_count
        self.last_updated = datetime.now()
        
        if additional_metrics:
            # Actualizar manteniendo la estructura
            self.additional_metrics = {
                'video_details': additional_metrics.get('video_details', self.additional_metrics.get('video_details', {})),
                'channel_details': additional_metrics.get('channel_details', self.additional_metrics.get('channel_details', {})),
                'start_time': additional_metrics.get('start_time', self.additional_metrics.get('start_time')),
                'end_time': additional_metrics.get('end_time', self.additional_metrics.get('end_time')),
                'scheduled_start': additional_metrics.get('scheduled_start', self.additional_metrics.get('scheduled_start')),
                'scheduled_end': additional_metrics.get('scheduled_end', self.additional_metrics.get('scheduled_end')),
                'chat_id': additional_metrics.get('chat_id', self.additional_metrics.get('chat_id')),
                'duration': additional_metrics.get('duration', self.additional_metrics.get('duration')),
                'status': additional_metrics.get('status', self.additional_metrics.get('status')),
                'privacy': additional_metrics.get('privacy', self.additional_metrics.get('privacy')),
                'license': additional_metrics.get('license', self.additional_metrics.get('license')),
                'embeddable': additional_metrics.get('embeddable', self.additional_metrics.get('embeddable')),
                'public_stats_viewable': additional_metrics.get('public_stats_viewable', self.additional_metrics.get('public_stats_viewable')),
                'made_for_kids': additional_metrics.get('made_for_kids', self.additional_metrics.get('made_for_kids')),
                'topics': additional_metrics.get('topics', self.additional_metrics.get('topics', []))
            }
        
        self.metrics_history.append({
            'timestamp': self.last_updated,
            'current_viewers': current_viewers,
            'total_views': total_views,
            'like_count': like_count,
            'comment_count': comment_count,
            'live_chat_messages': live_chat_messages,
            'subscriber_count': subscriber_count,
            'additional_metrics': self.additional_metrics
        }) 