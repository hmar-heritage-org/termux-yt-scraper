#!/usr/bin/env python3
"""
YouTube Comments Scraper for Hmar Conversational Corpora
Target Channel: B. Lalsanglien Inbuon Official (@lalsanglieninbuonofficial4410)
Preserves immutable raw data in JSONL format with complete metadata.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

CHANNEL_URL = "https://www.youtube.com/@lalsanglieninbuonofficial4410/videos"
CHANNEL_NAME = "B. Lalsanglien Inbuon Official"
OUTPUT_DIR = "/home/phxlm/Work/yt-comments/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "lalsanglien_inbuon_raw.jsonl")
TRACKING_FILE = os.path.join(OUTPUT_DIR, ".processed_videos.json")
YT_DLP = os.path.expanduser("~/.local/bin/yt-dlp")

def get_video_list():
    """Fetch list of all video IDs and titles from the channel."""
    print("Fetching channel video list...")
    cmd = [
        YT_DLP,
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s",
        CHANNEL_URL
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    videos = []
    for line in result.stdout.strip().split("\n"):
        if "\t" in line:
            vid, title = line.split("\t", 1)
            videos.append({"id": vid.strip(), "title": title.strip()})
    print(f"Total videos identified on channel: {len(videos)}")
    return videos

def load_processed_ids():
    """Load previously scraped video IDs to allow safe resumption."""
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    
    # Alternatively recover from existing JSONL output
    processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    if "video_id" in item:
                        processed.add(item["video_id"])
                except Exception:
                    continue
    return processed

def save_processed_ids(processed_set):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_set), f)

def scrape_video_comments(video_id, title):
    """Scrape comments for a single video using yt-dlp."""
    cmd = [
        YT_DLP,
        "--write-comments",
        "--skip-download",
        "--dump-single-json",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        if proc.returncode != 0:
            return []
        data = json.loads(proc.stdout)
        comments = data.get("comments")
        return comments if isinstance(comments, list) else []
    except Exception as e:
        print(f"  Warning: failed to scrape video {video_id}: {e}", file=sys.stderr)
        return []

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    videos = get_video_list()
    processed_ids = load_processed_ids()
    
    print(f"Previously scraped videos: {len(processed_ids)}")
    remaining = [v for v in videos if v["id"] not in processed_ids]
    print(f"Videos remaining to scrape: {len(remaining)}\n")
    
    total_comments_scraped = 0
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
        for idx, v in enumerate(remaining, 1):
            vid = v["id"]
            title = v["title"]
            print(f"[{idx}/{len(remaining)}] Scraping: {title[:55]}... ({vid})")
            
            raw_comments = scrape_video_comments(vid, title)
            saved_count = 0
            
            for c in raw_comments:
                record = {
                    "video_id": vid,
                    "video_title": title,
                    "channel": CHANNEL_NAME,
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
            save_processed_ids(processed_ids)
            total_comments_scraped += saved_count
            
            print(f"  -> {saved_count} comments saved (Session Total: {total_comments_scraped:,})")
            time.sleep(1.0) # Polite sleep to prevent throttling

    print("\n" + "="*50)
    print(f"Scraping completed! Total comments collected: {total_comments_scraped:,}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print("="*50)

if __name__ == "__main__":
    main()
