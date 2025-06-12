import os
from googleapiclient.discovery import build
from typing import Dict, Optional
from datetime import datetime

class YouTubeClient:
    def __init__(self):
        self.api_key = ""  # API key temporal
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_live_metrics(self, video_id: str) -> dict:
        """Obtiene las métricas en vivo que se actualizan cada 10 segundos"""
        try:
            # Obtener estadísticas del video
            video_response = self.youtube.videos().list(
                part='liveStreamingDetails,statistics',
                id=video_id
            ).execute()

            if not video_response['items']:
                print(f"No se encontraron métricas en vivo para el video ID: {video_id}")
                return {}

            video = video_response['items'][0]
            statistics = video.get('statistics', {})
            
            return {
                'current_viewers': int(video.get('liveStreamingDetails', {}).get('concurrentViewers', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'live_chat_messages': self._get_live_chat_message_count(video_id)
            }
        except Exception as e:
            print(f"Error al obtener métricas en vivo: {str(e)}")
            return {}

    def get_video_details(self, video_id: str) -> dict:
        """Obtiene los detalles del video que se actualizan cada 30 minutos"""
        try:
            print(f"Obteniendo detalles para el video ID: {video_id}")
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()

            if not video_response['items']:
                print(f"No se encontró información del video: {video_id}")
                return {}

            video = video_response['items'][0]
            snippet = video.get('snippet', {})

            return {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'published_at': snippet.get('publishedAt'),
                'thumbnails': snippet.get('thumbnails', {}),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId'),
                'start_time': video.get('liveStreamingDetails', {}).get('actualStartTime')
            }
        except Exception as e:
            print(f"Error al obtener detalles del video: {str(e)}")
            return {}

    def get_channel_details(self, video_id: str) -> dict:
        """Obtiene los detalles del canal que se actualizan cada 24 horas"""
        try:
            # Primero obtenemos el ID del canal desde el video
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()

            if not video_response['items']:
                return {}

            channel_id = video_response['items'][0]['snippet']['channelId']
            print(f"Channel ID obtenido: {channel_id}")

            # Luego obtenemos los detalles del canal
            channel_response = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()

            if not channel_response['items']:
                print(f"No se encontró información del canal: {channel_id}")
                return {}

            channel = channel_response['items'][0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})

            print(f"Información del canal obtenida: {snippet.get('title')}")
            return {
                'id': channel_id,
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'published_at': snippet.get('publishedAt'),
                'country': snippet.get('country'),
                'thumbnails': snippet.get('thumbnails', {}),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'keywords': snippet.get('keywords', ''),
                'custom_url': snippet.get('customUrl')
            }
        except Exception as e:
            print(f"Error al obtener detalles del canal: {str(e)}")
            return {}

    def _get_live_chat_message_count(self, video_id: str) -> int:
        """Obtiene la cantidad de mensajes en el chat en vivo"""
        try:
            video_response = self.youtube.videos().list(
                part='liveStreamingDetails',
                id=video_id
            ).execute()

            if not video_response['items']:
                return 0

            live_chat_id = video_response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
            if not live_chat_id:
                return 0

            chat_response = self.youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part='snippet',
                maxResults=1
            ).execute()

            return chat_response.get('pageInfo', {}).get('totalResults', 0)
        except Exception as e:
            print(f"Error al obtener mensajes del chat: {str(e)}")
            return 0

    def get_stream_details(self, video_id: str) -> dict:
        """Método principal que obtiene todos los detalles del stream"""
        live_metrics = self.get_live_metrics(video_id)
        video_details = self.get_video_details(video_id)
        channel_details = self.get_channel_details(video_id)

        return {
            'current_viewers': live_metrics.get('current_viewers', 0),
            'like_count': live_metrics.get('like_count', 0),
            'live_chat_messages': live_metrics.get('live_chat_messages', 0),
            'video_details': video_details,
            'channel_details': channel_details
        }

    def get_stream_details_old(self, video_id: str) -> Dict:
        """Obtiene todos los detalles disponibles de un stream en vivo y su canal"""
        try:
            print(f"Obteniendo detalles para el video ID: {video_id}")
            
            # Obtener información del video
            video_request = self.youtube.videos().list(
                part="snippet,liveStreamingDetails,statistics,contentDetails,status,topicDetails",
                id=video_id
            )
            video_response = video_request.execute()
            
            if not video_response.get('items'):
                print("No se encontraron items en la respuesta del video")
                return None
                
            video = video_response['items'][0]
            snippet = video.get('snippet', {})
            live_details = video.get('liveStreamingDetails', {})
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            status = video.get('status', {})
            topic_details = video.get('topicDetails', {})
            
            print(f"Información del video obtenida: {snippet.get('title')}")
            
            # Obtener información del canal
            channel_id = snippet.get('channelId')
            print(f"Channel ID obtenido: {channel_id}")
            
            channel_data = {}
            if channel_id:
                channel_request = self.youtube.channels().list(
                    part="snippet,statistics,brandingSettings",
                    id=channel_id
                )
                channel_response = channel_request.execute()
                if channel_response['items']:
                    channel = channel_response['items'][0]
                    channel_data = {
                        'id': channel.get('id'),
                        'snippet': channel.get('snippet', {}),
                        'statistics': channel.get('statistics', {}),
                        'brandingSettings': channel.get('brandingSettings', {})
                    }
                    print(f"Información del canal obtenida: {channel_data.get('snippet', {}).get('title')}")
                else:
                    print("No se encontraron items en la respuesta del canal")

            # Obtener comentarios en vivo si hay un chat activo
            live_chat_messages = 0
            chat_id = live_details.get('activeLiveChatId')
            if chat_id:
                try:
                    chat_request = self.youtube.liveChatMessages().list(
                        liveChatId=chat_id,
                        part="snippet",
                        maxResults=1
                    )
                    chat_response = chat_request.execute()
                    if chat_response.get('items'):
                        live_chat_messages = int(chat_response.get('pageInfo', {}).get('totalResults', 0))
                except Exception as e:
                    print(f"Error obteniendo chat en vivo: {str(e)}")

            result = {
                'title': snippet.get('title', 'Sin título'),
                'channel_title': snippet.get('channelTitle', 'Sin canal'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'current_viewers': int(live_details.get('concurrentViewers', 0)) if 'concurrentViewers' in live_details else 0,
                'total_views': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'live_chat_messages': live_chat_messages,
                'subscriber_count': int(channel_data.get('statistics', {}).get('subscriberCount', 0)),
                'video_details': {
                    'id': video_id,
                    'description': snippet.get('description', 'Sin descripción'),
                    'published_at': snippet.get('publishedAt'),
                    'thumbnails': snippet.get('thumbnails', {}),
                    'tags': snippet.get('tags', []),
                    'category_id': snippet.get('categoryId'),
                    'start_time': live_details.get('actualStartTime')
                },
                'channel_details': {
                    'id': channel_data.get('id'),
                    'title': channel_data.get('snippet', {}).get('title', 'Sin título'),
                    'description': channel_data.get('snippet', {}).get('description', 'Sin descripción'),
                    'published_at': channel_data.get('snippet', {}).get('publishedAt'),
                    'country': channel_data.get('snippet', {}).get('country'),
                    'thumbnails': channel_data.get('snippet', {}).get('thumbnails', {}),
                    'subscriber_count': int(channel_data.get('statistics', {}).get('subscriberCount', 0)),
                    'video_count': int(channel_data.get('statistics', {}).get('videoCount', 0)),
                    'view_count': int(channel_data.get('statistics', {}).get('viewCount', 0)),
                    'keywords': channel_data.get('brandingSettings', {}).get('channel', {}).get('keywords', ''),
                    'custom_url': channel_data.get('snippet', {}).get('customUrl')
                },
                'additional_metrics': {
                    'start_time': live_details.get('actualStartTime'),
                    'end_time': live_details.get('actualEndTime'),
                    'scheduled_start': live_details.get('scheduledStartTime'),
                    'scheduled_end': live_details.get('scheduledEndTime'),
                    'chat_id': live_details.get('activeLiveChatId'),
                    'duration': content_details.get('duration'),
                    'status': status.get('uploadStatus'),
                    'privacy': status.get('privacyStatus'),
                    'license': status.get('license'),
                    'embeddable': status.get('embeddable'),
                    'public_stats_viewable': status.get('publicStatsViewable'),
                    'made_for_kids': status.get('madeForKids'),
                    'topics': topic_details.get('topicCategories', [])
                }
            }
            
            print("Datos del video:", result['video_details'])
            print("Datos del canal:", result['channel_details'])
            
            return result
        except Exception as e:
            print(f"Error fetching stream details: {str(e)}")
            return None 