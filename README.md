# Hmar Heritage Foundation — YouTube Comment Scraper (Termux & Linux)

A lightweight, resilient CLI tool to scrape raw conversational comments from YouTube channels, playlists, or videos. Designed to collect real-world contemporary Hmar and Zo language text for NLP corpora and language models.

---

## Key Features

1. **Direct Android WhatsApp Integration:**
   * On Android Termux, scrapes directly into `/sdcard/Download/Hmar-YT-Comments/`.
   * Volunteers can immediately open WhatsApp $\rightarrow$ Attach $\rightarrow$ Document $\rightarrow$ Downloads and share the `.jsonl` file.
2. **Android Wake Lock (`termux-wake-lock`):**
   * Automatically keeps Android awake so the phone screen can turn off safely without pausing or killing the scraper.
3. **Resilient Auto-Resume:**
   * Keeps track of scraped video IDs in `.state_[channel].json`. 
   * If paused, interrupted, or stopped, re-running automatically resumes where it left off.
4. **Fault-Tolerant:**
   * Automatically skips videos with disabled comments, private videos, or deleted content.
   * Flushes comments to disk after every single video.
5. **No API Keys Needed:**
   * Operates via `yt-dlp` headless scraping with zero quota restrictions.

---

## Quick Setup on Android Termux

Copy and paste this into Termux:

```bash
pkg update -y && pkg install -y git python ffmpeg termux-api
pip install --upgrade yt-dlp
termux-setup-storage
```

Clone the repository and run:

```bash
git clone https://github.com/hmar-heritage-org/termux-yt-scraper.git
cd termux-yt-scraper
python termux_yt_scraper.py
```

*(Or run `bash install.sh` to get the instant `hmar-yt-scrape` command).*

---

## Running on Linux / PC

```bash
pip install yt-dlp
python3 termux_yt_scraper.py
```

Outputs will be saved in `./raw/[channel_name]_raw.jsonl`.

---

## Raw Data Schema (JSONL)

Each line in the `.jsonl` file is a complete JSON object:

```json
{
  "video_id": "I1sUNM-9EZY",
  "video_title": "LALPA INPAK HI LUNGAWINA A NIH...",
  "channel": "B. Lalsanglien Inbuon Official",
  "comment_id": "Ugx...",
  "author": "@user123",
  "author_id": "UC...",
  "text": "Nitin veltam ka ngai, athu hin ka lugril laimu tak hi athem nasa...",
  "likes": 14,
  "timestamp": 1690000000,
  "time_text": "1 year ago",
  "is_favorited": false,
  "scraped_at": "2026-09-16T06:15:00+00:00"
}
```
