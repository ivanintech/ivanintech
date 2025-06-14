import logging
import re
from typing import Optional, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class YouTubeResource(BaseModel):
    id: str
    title: str
    description: str
    thumbnail_url: str
    kind: str # 'video' or 'channel'

def get_youtube_resource_details(url: str) -> Optional[YouTubeResource]:
    """
    Gets the details of a YouTube resource (video or channel) from a URL.
    """
    if not settings.YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY is not configured. YouTube service will not work.")
        return None

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=settings.YOUTUBE_API_KEY)

        # Identify if it's a video or a channel and extract the ID
        video_id = _extract_video_id(url)
        channel_id = _extract_channel_id(url)

        if video_id:
            return _get_video_details(youtube, video_id)
        elif channel_id:
            return _get_channel_details(youtube, channel_id)
        else:
            logger.info(f"The URL does not appear to be a valid YouTube video or channel: {url}")
            return None

    except HttpError as e:
        logger.error(f"YouTube API error: {e.content}", exc_info=True)
        # If it's a quota error, we might want to handle it differently
        if e.resp.status == 403:
            logger.error("YouTube API 403 error: Check quota or API Key configuration.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in YouTube service: {e}", exc_info=True)
        return None

def _extract_video_id(url: str) -> Optional[str]:
    """Extracts the video ID from a YouTube URL more robustly."""
    # Unified pattern that covers various YouTube URL formats
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def _extract_channel_id(url: str) -> Optional[str]:
    """Extracts the channel ID or handle from a YouTube URL."""
    # Prioritizes handles (@) and then channel IDs (UC...)
    patterns = {
        'handle': r"(?:youtube\.com\/)(@[\w.-]+)",
        'channel_id': r"(?:youtube\.com\/channel\/)(UC[\w-]+)",
    }
    
    match = re.search(patterns['handle'], url)
    if match: return match.group(1)

    match = re.search(patterns['channel_id'], url)
    if match: return match.group(1)
    
    # Fallback for legacy /c/name URLs
    match = re.search(r"(?:youtube\.com\/c\/)([\w-]+)", url)
    if match: return match.group(1)

    return None

def _get_video_details(youtube, video_id: str) -> Optional[YouTubeResource]:
    """Gets the details of a specific video."""
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    
    if not response.get("items"):
        return None

    video_item = response["items"][0]["snippet"]
    thumbnail = video_item["thumbnails"].get("standard", video_item["thumbnails"].get("high", {}))
    return YouTubeResource(
        id=video_id,
        title=video_item["title"],
        description=video_item["description"],
        thumbnail_url=thumbnail.get("url"),
        kind="video"
    )

def _get_channel_details(youtube, channel_identifier: str) -> Optional[YouTubeResource]:
    """Gets the details of a specific channel using its ID, handle, or custom URL."""
    request_params = {'part': "snippet"}
    
    if channel_identifier.startswith('@'):
        request_params['forHandle'] = channel_identifier.replace('@', '')
    elif channel_identifier.startswith('UC'):
        request_params['id'] = channel_identifier
    else:
        # For old custom URLs, search by username (ID)
        request_params['forUsername'] = channel_identifier

    request = youtube.channels().list(**request_params)
    response = request.execute()

    if not response.get("items"):
        logger.warning(f"No channel found for identifier: {channel_identifier}")
        return None

    channel_item = response["items"][0]
    snippet = channel_item["snippet"]
    thumbnail = snippet["thumbnails"].get("high", snippet["thumbnails"].get("default", {}))
    
    return YouTubeResource(
        id=channel_item["id"],
        title=snippet["title"],
        description=snippet["description"],
        thumbnail_url=thumbnail.get("url"),
        kind="channel"
    )