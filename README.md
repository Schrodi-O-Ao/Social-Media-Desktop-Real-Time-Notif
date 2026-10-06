# Aoo

Aoo sits near the Windows clock and watches the YouTube channels you choose. When a new upload arrives, it shows a small window. Click the window to open the video.

Make a `.env` file beside `aoo.py`:

```text
YOUTUBE_API_KEY=put-your-key-here
```

The key comes from a Google Cloud project with YouTube Data API v3 enabled. Keep `.env` private.

Install and start Aoo:

```powershell
py -m pip install -r requirements.txt
py aoo.py
```

Right-click the Aoo tray icon. `Channels` opens the small channel editor. Add a real channel ID, such as `UC...`; a handle like `@name` is not a channel ID. `Check now` checks without waiting for the normal 15-minute interval.

The first successful check records the channel’s current upload and stays quiet. That avoids alerts for old videos. Aoo saves its channel list and last seen video locally in `channels.json` and `last_seen.json`.

`start_aoo.bat` starts the same app when double-clicked. Put a shortcut to it in `shell:startup` if you want it to run after Windows sign-in.

## Where it can grow

The code separates YouTube requests, saved data, and the Tk interface. That makes new sources possible, but each source should expose the same small idea: find its newest item, give it a stable ID, title, link, and optional picture. Add that behind a provider interface before adding Twitch, RSS, or another site.

For a more polished Windows feel, native Windows toast notifications are the next useful step. They can appear in notification history and need less custom window handling. Per-channel schedules and failures belong in saved settings only after the basic flow stays reliable.
