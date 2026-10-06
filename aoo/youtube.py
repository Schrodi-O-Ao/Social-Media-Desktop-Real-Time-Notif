from dataclasses import dataclass

import requests

from .models import Video


class YouTubeError(RuntimeError):
    """A YouTube request failed or returned data Aoo cannot use."""

    pass


@dataclass
class YouTubeClient:
    """Ask YouTube for the newest upload from one channel."""

    api_key: str
    timeout: float = 15.0

    def __post_init__(self) -> None:
        self.session = requests.Session()

    def latest_video(self, channel_id: str) -> Video | None:
        """Return the newest upload, or None when the channel has no uploads."""
        uploads_id = self._uploads_playlist(channel_id)
        if not uploads_id:
            return None
        data = self._get("playlistItems", {"part": "snippet,contentDetails", "playlistId": uploads_id, "maxResults": 1})
        items = data.get("items", [])
        if not items:
            return None
        item = items[0]
        snippet = item.get("snippet", {})
        video_id = item.get("contentDetails", {}).get("videoId")
        if not isinstance(video_id, str) or not video_id:
            return None
        thumbnails = snippet.get("thumbnails", {})
        thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}
        return Video(video_id, str(snippet.get("title", "Untitled video")),
                     str(snippet.get("videoOwnerChannelTitle") or snippet.get("channelTitle") or channel_id),
                     thumbnail.get("url") if isinstance(thumbnail, dict) else None)

    def _uploads_playlist(self, channel_id: str) -> str | None:
        """Find YouTube's upload list for a channel.

        Reading this list is much cheaper than repeatedly searching YouTube.
        """
        data = self._get("channels", {"part": "contentDetails", "id": channel_id, "maxResults": 1})
        items = data.get("items", [])
        if not items:
            return None
        value = items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        return value if isinstance(value, str) else None

    def _get(self, resource: str, parameters: dict[str, object]) -> dict:
        try:
            response = self.session.get(f"https://www.googleapis.com/youtube/v3/{resource}",
                                        params={**parameters, "key": self.api_key}, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise YouTubeError(str(error)) from error
        if not isinstance(data, dict):
            raise YouTubeError("YouTube returned an unexpected response.")
        return data
