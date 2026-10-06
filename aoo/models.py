from dataclasses import dataclass


@dataclass(frozen=True)
class Channel:
    """One YouTube channel chosen by the user."""

    channel_id: str
    name: str


@dataclass(frozen=True)
class Video:
    """The small amount of video data needed for an Aoo alert."""

    video_id: str
    title: str
    channel_name: str
    thumbnail_url: str | None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"
