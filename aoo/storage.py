import json
import os
from pathlib import Path

from .models import Channel


class Store:
    """Read and save Aoo's small JSON files."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.channels_file = folder / "channels.json"
        self.state_file = folder / "last_seen.json"

    def load_channels(self) -> list[Channel]:
        """Read channels, including the old file shape used by earlier Aoo builds."""
        data = self._read(self.channels_file, [])
        if not isinstance(data, list):
            return []
        channels = []
        for item in data:
            if not isinstance(item, dict):
                continue
            channel_id = str(item.get("channel_id", item.get("channelID", ""))).strip()
            name = str(item.get("name", item.get("channelName", channel_id))).strip()
            if channel_id:
                channels.append(Channel(channel_id, name or channel_id))
        return channels

    def save_channels(self, channels: list[Channel]) -> None:
        self._write(self.channels_file, [
            {"channel_id": channel.channel_id, "name": channel.name}
            for channel in channels
        ])

    def load_seen(self) -> dict[str, str]:
        data = self._read(self.state_file, {})
        return data if isinstance(data, dict) else {}

    def save_seen(self, seen: dict[str, str]) -> None:
        self._write(self.state_file, seen)

    @staticmethod
    def _read(path: Path, default: object) -> object:
        try:
            with path.open(encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return default

    def _write(self, path: Path, data: object) -> None:
        """Replace a complete file so a stopped save does not leave broken JSON."""
        self.folder.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
            file.write("\n")
        os.replace(temporary, path)
