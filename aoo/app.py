import io
import os
import queue
import re
import threading
import webbrowser
from pathlib import Path

import pystray
import tkinter as tk
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageOps, ImageTk
from tkinter import messagebox, ttk

from .models import Channel, Video
from .storage import Store
from .youtube import YouTubeClient, YouTubeError

CHECK_EVERY_MS = 15 * 60 * 1000
CHANNEL_ID = re.compile(r"^UC[\w-]{22}$")
CHECK_FINISHED = object()


class AooApp:
    """Keep the tray icon, channel data, checks, and windows together."""

    def __init__(self, root: tk.Tk, api_key: str, folder: Path) -> None:
        self.root = root
        self.store = Store(folder)
        self.client = YouTubeClient(api_key)
        self.channels = self.store.load_channels()
        self.seen = self.store.load_seen()
        # Background work puts results here. Tk reads them on its own thread.
        self.events: queue.Queue[Video | str | object] = queue.Queue()
        # Tray menu callbacks are not Tk callbacks, so they use this queue too.
        self.commands: queue.Queue[str] = queue.Queue()
        self.stopping = threading.Event()
        self.checking = False
        self.window: tk.Toplevel | None = None
        self.root.withdraw()
        self.icon = self._make_tray_icon()

    def run(self) -> None:
        """Start the tray icon and the hidden Tk event loop."""
        self.icon.run_detached()
        self._schedule_check(0)
        self.root.after(250, self._handle_events)
        self.root.after(100, self._handle_commands)
        self.root.mainloop()

    def _make_tray_icon(self) -> pystray.Icon:
        image = Image.new("RGB", (64, 64), "#2563eb")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((5, 5, 59, 59), radius=13, fill="#1d4ed8")
        draw.text((20, 20), "AO", fill="white")
        menu = pystray.Menu(
            pystray.MenuItem("Channels", lambda: self.commands.put("channels")),
            pystray.MenuItem("Check now", lambda: self.commands.put("check")),
            pystray.MenuItem("Quit", lambda: self.commands.put("quit")),
        )
        return pystray.Icon("Aoo", image, "Aoo", menu)

    def _schedule_check(self, delay: int = CHECK_EVERY_MS) -> None:
        if not self.stopping.is_set():
            self.root.after(delay, self.check_now)

    def check_now(self) -> None:
        """Check in the background so the tray and channel window still respond."""
        if self.checking or self.stopping.is_set():
            return
        self.checking = True
        threading.Thread(target=self._check_channels, daemon=True).start()

    def _check_channels(self) -> None:
        try:
            for channel in list(self.channels):
                try:
                    video = self.client.latest_video(channel.channel_id)
                except YouTubeError as error:
                    self.events.put(f"Could not check {channel.name}: {error}")
                    continue
                if video is None:
                    self.events.put(f"No YouTube channel found for {channel.channel_id}.")
                    continue
                old_video_id = self.seen.get(channel.channel_id)
                if old_video_id is None:
                    # The first check learns the current video. It is not an alert.
                    self.seen[channel.channel_id] = video.video_id
                elif old_video_id != video.video_id:
                    self.seen[channel.channel_id] = video.video_id
                    self.events.put(video)
            self.store.save_seen(self.seen)
        finally:
            self.checking = False
            self.events.put(CHECK_FINISHED)

    def _handle_commands(self) -> None:
        while not self.commands.empty():
            command = self.commands.get_nowait()
            if command == "channels":
                self.open_channels()
            elif command == "check":
                self.check_now()
            elif command == "quit":
                self.quit()
                return
        if not self.stopping.is_set():
            self.root.after(100, self._handle_commands)

    def _handle_events(self) -> None:
        while not self.events.empty():
            event = self.events.get_nowait()
            if isinstance(event, Video):
                self.show_notification(event)
            elif event is CHECK_FINISHED:
                self._schedule_check()
            else:
                print(event)
        if not self.stopping.is_set():
            self.root.after(250, self._handle_events)

    def open_channels(self) -> None:
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            return
        self.window = ChannelWindow(self, self.root)

    def add_channel(self, channel_id: str, name: str) -> str | None:
        channel_id = channel_id.strip()
        if not CHANNEL_ID.fullmatch(channel_id):
            return "Use a YouTube channel ID starting with UC."
        if any(item.channel_id == channel_id for item in self.channels):
            return "That channel is already here."
        self.channels.append(Channel(channel_id, name.strip() or channel_id))
        self.store.save_channels(self.channels)
        self.check_now()
        return None

    def remove_channel(self, channel_id: str) -> None:
        self.channels = [item for item in self.channels if item.channel_id != channel_id]
        self.seen.pop(channel_id, None)
        self.store.save_channels(self.channels)
        self.store.save_seen(self.seen)

    def show_notification(self, video: Video) -> None:
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except (ImportError, RuntimeError):
            pass
        NotificationWindow(self.root, video)

    def quit(self) -> None:
        self.stopping.set()
        self.icon.stop()
        self.root.quit()
        self.root.destroy()


class ChannelWindow(tk.Toplevel):
    """Let the user add or remove the channels Aoo watches."""

    def __init__(self, app: AooApp, master: tk.Tk) -> None:
        super().__init__(master)
        self.app = app
        self.title("Aoo channels")
        self.geometry("620x390")
        self.minsize(520, 320)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="YouTube channels", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10)
        )
        self.table = ttk.Treeview(self, columns=("name", "id"), show="headings", selectmode="browse")
        self.table.heading("name", text="Name")
        self.table.heading("id", text="Channel ID")
        self.table.column("name", width=190)
        self.table.column("id", width=370)
        self.table.grid(row=1, column=0, sticky="nsew", padx=20)
        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=0, sticky="ew", padx=20, pady=16)
        ttk.Button(buttons, text="Add channel", command=self.add_dialog).pack(side="left")
        ttk.Button(buttons, text="Remove selected", command=self.remove_selected).pack(side="left", padx=8)
        ttk.Button(buttons, text="Check now", command=app.check_now).pack(side="right")
        self.refresh()

    def refresh(self) -> None:
        self.table.delete(*self.table.get_children())
        for channel in self.app.channels:
            self.table.insert("", "end", iid=channel.channel_id, values=(channel.name, channel.channel_id))

    def add_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add a channel")
        dialog.transient(self)
        dialog.grab_set()
        ttk.Label(dialog, text="Channel ID").grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        channel_id = ttk.Entry(dialog, width=42)
        channel_id.grid(row=1, column=0, padx=16)
        ttk.Label(dialog, text="Name (optional)").grid(row=2, column=0, sticky="w", padx=16, pady=(12, 4))
        name = ttk.Entry(dialog, width=42)
        name.grid(row=3, column=0, padx=16)

        def save() -> None:
            error = self.app.add_channel(channel_id.get(), name.get())
            if error:
                messagebox.showerror("Could not add channel", error, parent=dialog)
                return
            self.refresh()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, sticky="e", padx=16, pady=16)
        channel_id.focus_set()

    def remove_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            return
        channel_id = selected[0]
        if messagebox.askyesno("Remove channel", "Stop watching this channel?", parent=self):
            self.app.remove_channel(channel_id)
            self.refresh()


class NotificationWindow(tk.Toplevel):
    """Show one new upload and open it when the popup is clicked."""

    def __init__(self, master: tk.Tk, video: Video) -> None:
        super().__init__(master, bg="#172033")
        self.video = video
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        width, height = 430, 142
        x = self.winfo_screenwidth() - width - 24
        self.geometry(f"{width}x{height}+{x}+24")
        self._image = self._load_image(video.thumbnail_url)
        thumbnail = tk.Label(self, image=self._image, bg="#172033")
        thumbnail.grid(row=0, column=0, rowspan=3, padx=14, pady=14)
        tk.Label(self, text=video.channel_name, fg="#93c5fd", bg="#172033", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="sw", pady=(18, 0))
        tk.Label(self, text=video.title, fg="white", bg="#172033", justify="left", wraplength=260, font=("Segoe UI", 10)).grid(row=1, column=1, sticky="nw", pady=4)
        tk.Label(self, text="Open video", fg="#aab7cf", bg="#172033", font=("Segoe UI", 9)).grid(row=2, column=1, sticky="nw")
        tk.Button(self, text="×", command=self.destroy, borderwidth=0, bg="#172033", fg="white", activebackground="#172033", activeforeground="white").place(x=400, y=7)
        for widget in (self, thumbnail):
            widget.bind("<Button-1>", self.open_video)
        self.after(30_000, self.destroy)

    @staticmethod
    def _load_image(url: str | None) -> ImageTk.PhotoImage:
        image = Image.new("RGB", (120, 90), "#2563eb")
        if url:
            try:
                import requests
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
            except (OSError, requests.RequestException):
                pass
        return ImageTk.PhotoImage(ImageOps.fit(image, (120, 90)))

    def open_video(self, _event: object) -> None:
        webbrowser.open_new_tab(self.video.url)
        self.destroy()


def main() -> None:
    """Load the key, then start the desktop app."""
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Set YOUTUBE_API_KEY in .env, then run Aoo again.")
        return
    root = tk.Tk()
    root.withdraw()
    AooApp(root, api_key, Path(__file__).resolve().parent.parent).run()
