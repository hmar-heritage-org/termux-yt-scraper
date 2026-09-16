# termux-yt-scraper

A simple script to scrape YouTube comments from channels, playlists, or videos. Built for Termux on Android and Linux to help collect modern, conversational Hmar text for language research.

## How it works

- Enter any YouTube channel, playlist, or video link.
- The script grabs comments and writes them to a JSONL file.
- On Android, it saves files straight to `Downloads/Hmar-YT-Comments/` so you can attach and send them over WhatsApp without digging through system folders.
- It keeps your phone awake while running (`termux-wake-lock`) so you can turn the screen off safely.
- If you stop the script, running it again picks up where it left off.

## Android (Termux) setup

1. Install dependencies and grant storage access:

```bash
pkg update -y && pkg install -y git python ffmpeg termux-api
pip install --upgrade yt-dlp
termux-setup-storage
```

2. Clone and run:

```bash
git clone https://github.com/hmar-heritage-org/termux-yt-scraper.git
cd termux-yt-scraper
python main.py
```

You can also run `bash install.sh` to add `hmar-yt-scrape` as a shortcut command in Termux.

3. Sharing the output:
Once the scrape finishes or you pause it, open WhatsApp, go to Document, navigate to `Downloads/Hmar-YT-Comments/`, and send the `.jsonl` file.

## Running on Linux or PC

```bash
pip install yt-dlp
python3 main.py
```

Files are saved in `./raw/`.

For scraping a single channel directly with a hardcoded script, you can also run:

```bash
python3 channel.py
```

## Output format

Each comment is saved as one JSON line in `[channel_name]_raw.jsonl`:

```json
{
  "video_id": "I1sUNM-9EZY",
  "video_title": "Sample Song Title",
  "channel": "Channel Name",
  "comment_id": "Ugx...",
  "author": "@username",
  "author_id": "UC...",
  "text": "Ka lungril laimu tak hi athem nasa...",
  "likes": 14,
  "timestamp": 1690000000,
  "time_text": "1 year ago",
  "is_favorited": false,
  "scraped_at": "2026-09-16T06:15:00+00:00"
}
```
