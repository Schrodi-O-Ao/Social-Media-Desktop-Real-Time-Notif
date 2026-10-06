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

## Check or remove Aoo

These are PowerShell scripts. Open PowerShell in this project folder and run:

```powershell
.\scripts\Test-Aoo.ps1
```

It tells you whether this Aoo project and its saved data exist.

This removes only your saved channels and video history. It does not remove the code:

```powershell
.\scripts\Remove-Aoo.ps1 -DataOnly
```

This removes the whole verified Aoo project folder, including the scripts themselves. Close Aoo first. The script asks you to type `REMOVE` before it does anything:

```powershell
.\scripts\Remove-Aoo.ps1
```

If PowerShell blocks a local script, run it once with `-ExecutionPolicy Bypass`, for example:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\Test-Aoo.ps1
```

