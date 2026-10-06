# Start Aoo

Install the packages once:

```powershell
py -m pip install -r requirements.txt
```

Put this in a file named `.env` in this folder:

```text
YOUTUBE_API_KEY=your-key
```

Run `py aoo.py` or double-click `start_aoo.bat`.

Find the blue Aoo icon near the Windows clock. Right-click it, open `Channels`, then add the channel ID from a URL shaped like `youtube.com/channel/UC...`. Give it a short name if you want.

Nothing pops up on the first check. Aoo uses that check to learn what is already there. Later uploads make a pop-up; click it to open the video.

If Aoo exits at once, the API key is missing. If it stays open but does not check a channel, open `Channels` and make sure the ID starts with `UC`. The app writes details about failed checks to the terminal window that started it.
