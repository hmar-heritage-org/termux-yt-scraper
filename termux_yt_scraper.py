#!/usr/bin/env python3
"""
Hmar Heritage Foundation — YouTube Comments Corpus Scraper for Termux / Linux
Extracts raw conversational comments from channels, playlists, or videos.
Saves directly to Android Download folder for easy WhatsApp sharing.
"""

import os
import sys
import re
import json
import time
import shutil
import atexit
import signal
import subprocess
from datetime import datetime, timezone

# ---------------------------------------------------------
# Platform & Storage Path Detection
# ---------------------------------------------------------
IS_ANDROID = os.path.exists("/data/data/com.termux")

if IS_ANDROID:
    # On Android Termux: save directly to shared Downloads
    STORAGE_BASE = "/sdcard/Download/Hmar-YT-Comments"
else:
    # On Linux PC: save to local raw folder
    STORAGE_BASE = os.path.abspath("./raw")

YT_DLP_BIN = shutil.which("yt-dlp") or os.path.expanduser("~/.local/bin/yt-dlp")

# ---------------------------------------------------------
# Termux Wake Lock Management
# ---------------------------------------------------------
def acquire_wake_lock():
    """Acquire Android wake lock so process is not suspended when screen turns off."""
    if IS_ANDROID and shutil.which("termux-wake-lock"):
        try:
            subprocess.run(["termux-wake-lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("  [✓] Android wake lock active (screen can turn off safely)")
        except Exception:
            pass

def release_wake_lock():
    """Release Android wake lock when process terminates."""
    if IS_ANDROID and shutil.which("termux-wake-unlock"):
        try:
            subprocess.run(["termux-wake-unlock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

atexit.register(release_wake_lock)

def handle_sigint(sig, frame):
    print("\n\n[!] Process interrupted by user. Exiting safely...")
    release_wake_lock()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def sanitize_filename(name):
    """Sanitize channel or video title for safe file naming."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', "_", name)
    return name.strip("._") or "youtube_data"

def get_channel_info(url):
    """Inspect the URL to get the clean title and video list."""
    print("\n[+] Inspecting YouTube target...")
    cmd = [
        YT_DLP_BIN,
        "--flat-playlist",
        "--print", "%(playlist_title,channel,title)s\t%(id)s\t%(title)s",
        url
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[-] Error fetching target info: {e.stderr.strip()}")
        return None, []

    videos = []
    channel_name = None

    for line in proc.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            c_name, vid, v_title = parts[0], parts[1], parts[2]
            if not channel_name and c_name and c_name != "NA":
                channel_name = c_name
            videos.append({"id": vid.strip(), "title": v_title.strip()})
        elif len(parts) == 2:
            vid, v_title = parts[0], parts[1]
            videos.append({"id": vid.strip(), "title": v_title.strip()})

    if not channel_name:
        # Fallback extract from URL if @handle
        handle_match = re.search(r'(@[a-zA-Z0-9_\-\.]+)', url)
        channel_name = handle_match.group(1) if handle_match else "scraped_channel"

    return channel_name, videos

def load_processed_ids(state_file):
    """Load list of already scraped video IDs for resume support."""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_processed_ids(state_file, processed_set):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(list(processed_set), f)

def scrape_single_video(video_id):
    """Fetch comments for a video using yt-dlp."""
    cmd = [
        YT_DLP_BIN,
        "--write-comments",
        "--skip-download",
        "--dump-single-json",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
        if proc.returncode != 0:
            return []
        data = json.loads(proc.stdout)
        comments = data.get("comments")
        return comments if isinstance(comments, list) else []
    except Exception:
        return []

# ---------------------------------------------------------
# Main Execution Loop
# ---------------------------------------------------------
def main():
    print("=" * 60)
    print("   Hmar Heritage Foundation — YouTube Comment Scraper")
    print("=" * 60)

    # Check yt-dlp
    if not shutil.which("yt-dlp") and not os.path.exists(YT_DLP_BIN):
        print("[-] Error: yt-dlp is not installed!")
        print("    Install it via: pip install yt-dlp")
        sys.exit(1)

    # Acquire wake lock if in Termux
    acquire_wake_lock()

    # Prompt user for URL
    print("\nEnter a YouTube Channel URL, Playlist URL, or Video link:")
    print("Examples:")
    print("  • https://www.youtube.com/@lalsanglieninbuonofficial4410")
    print("  • @lalsanglieninbuonofficial4410")
    print("  • https://www.youtube.com/watch?v=...")
    
    try:
        target_url = input("\nTarget URL: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)

    if not target_url:
        print("[-] No URL provided. Exiting.")
        sys.exit(1)

    # Normalize bare handle like @channel
    if target_url.startswith("@"):
        target_url = f"https://www.youtube.com/{target_url}/videos"
    elif "/@" in target_url and not target_url.endswith("/videos"):
        target_url = f"{target_url.rstrip('/')}/videos"

    channel_name, videos = get_channel_info(target_url)
    if not videos:
        print("[-] No videos found for this URL. Check the link and try again.")
        sys.exit(1)

    clean_channel = sanitize_filename(channel_name)
    os.makedirs(STORAGE_BASE, exist_ok=True)

    output_file = os.path.join(STORAGE_BASE, f"{clean_channel}_raw.jsonl")
    state_file = os.path.join(STORAGE_BASE, f".state_{clean_channel}.json")

    processed_ids = load_processed_ids(state_file)
    remaining_videos = [v for v in videos if v["id"] not in processed_ids]

    print(f"\n[+] Channel Target:   {channel_name}")
    print(f"[+] Total Videos:     {len(videos)}")
    print(f"[+] Already Scraped:  {len(processed_ids)}")
    print(f"[+] Remaining:        {len(remaining_videos)}")
    print(f"[+] Output File:      {output_file}")
    print("-" * 60)

    if not remaining_videos:
        print("\n[✓] All videos in this channel have already been scraped!")
        print(f"    File: {output_file}")
        sys.exit(0)

    total_scraped_session = 0

    with open(output_file, "a", encoding="utf-8") as out_f:
        for idx, v in enumerate(remaining_videos, 1):
            vid = v["id"]
            vtitle = v["title"]
            
            print(f"\n[{idx}/{len(remaining_videos)}] Scraping: {vtitle[:50]}... ({vid})")
            
            comments = scrape_single_video(vid)
            saved_count = 0

            for c in comments:
                record = {
                    "video_id": vid,
                    "video_title": vtitle,
                    "channel": channel_name,
                    "comment_id": c.get("id"),
                    "author": c.get("author"),
                    "author_id": c.get("author_id"),
                    "text": c.get("text"),
                    "likes": c.get("like_count", 0),
                    "timestamp": c.get("timestamp"),
                    "time_text": c.get("time_text"),
                    "is_favorited": c.get("is_favorited", False),
                    "scraped_at": datetime.now(timezone.utc).isoformat()
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                saved_count += 1

            out_f.flush()
            processed_ids.add(vid)
            save_processed_ids(state_file, processed_ids)
            total_scraped_session += saved_count

            print(f"  └── Saved {saved_count} comments (Session Total: {total_scraped_session:,})")
            time.sleep(1.0) # Polite pacing

    print("\n" + "=" * 60)
    print("   SCRAPING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Total Comments Gathered: {total_scraped_session:,}")
    print(f"Saved to: {output_file}")
    
    if IS_ANDROID:
        print("\n[★] HOW TO SEND VIA WHATSAPP:")
        print("  1. Open WhatsApp and select the chat / group.")
        print("  2. Tap the '+' or paperclip icon -> Document.")
        print(f"  3. Go to: Downloads -> Hmar-YT-Comments -> {os.path.basename(output_file)}")
        print("  4. Send the file!")
    print("=" * 60)

if __name__ == "__main__":
    main()
