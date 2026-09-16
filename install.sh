#!/data/data/com.termux/files/usr/bin/bash
# =========================================================
# Hmar Heritage Foundation — YouTube Comment Scraper Setup
# 1-Command Installer for Termux
# =========================================================

set -e

echo "====================================================="
echo "   Hmar Heritage Foundation — Termux Scraper Setup"
echo "====================================================="

echo "[1/4] Updating package repositories..."
pkg update -y

echo "[2/4] Installing Python, FFmpeg, and Termux tools..."
pkg install -y python ffmpeg termux-api

echo "[3/4] Installing yt-dlp..."
pip install --upgrade yt-dlp

echo "[4/4] Requesting phone storage access..."
termux-setup-storage || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR/termux_yt_scraper.py"

# Create global shortcut command 'hmar-yt-scrape'
if [ -d "$PREFIX/bin" ]; then
    ln -sf "$SCRIPT_DIR/termux_yt_scraper.py" "$PREFIX/bin/hmar-yt-scrape"
    echo ""
    echo "====================================================="
    echo " [✓] Installation Complete!"
    echo " You can now run the tool from anywhere by typing:"
    echo ""
    echo "     hmar-yt-scrape"
    echo ""
    echo "====================================================="
else
    echo "Run with: python3 $SCRIPT_DIR/termux_yt_scraper.py"
fi
