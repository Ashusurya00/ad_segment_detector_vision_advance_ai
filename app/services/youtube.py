"""
YouTube video download and metadata extraction via yt-dlp.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Optional

from app.api.schemas import MediaInfo, Platform, VideoKind
from app.utils.log import get_logger, log_stage

logger = get_logger("youtube")

# URL patterns
_YT_LONG = re.compile(r"(youtube\.com/watch\?v=|youtu\.be/)")
_YT_SHORT = re.compile(r"youtube\.com/shorts/")


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube video."""
    return bool(_YT_LONG.search(url) or _YT_SHORT.search(url))


def detect_youtube_kind(url: str) -> VideoKind:
    """Detect if a YouTube URL is a short or long-form video."""
    if _YT_SHORT.search(url):
        return VideoKind.SHORT
    return VideoKind.VOD


def download_youtube(
    url: str,
    output_dir: Optional[str] = None,
) -> MediaInfo:
    """
    Download a YouTube video and return media info.

    Uses yt-dlp to download the best available format with both
    video and audio streams.

    Args:
        url: YouTube URL
        output_dir: Directory to save the downloaded file

    Returns:
        MediaInfo with paths and metadata
    """
    import yt_dlp

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="ad_detect_")

    output_path = str(Path(output_dir) / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    with log_stage(logger, "youtube_download", url=url):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise ValueError(f"Failed to extract info from {url}")

            # Resolve actual downloaded file path
            video_path = ydl.prepare_filename(info)
            # yt-dlp may change extension
            p = Path(video_path)
            if not p.exists():
                # Try common extensions
                for ext in ["mp4", "webm", "mkv"]:
                    alt = p.with_suffix(f".{ext}")
                    if alt.exists():
                        video_path = str(alt)
                        break

            duration = info.get("duration", 0) or 0
            kind = detect_youtube_kind(url)

            # If duration is very short but was classified as VOD, recheck
            if kind == VideoKind.VOD and duration <= 90:
                kind = VideoKind.SHORT

            return MediaInfo(
                video_path=video_path,
                audio_path=None,  # extracted later
                url=url,
                platform=Platform.YOUTUBE,
                kind=kind,
                duration_s=float(duration),
                title=info.get("title", ""),
                width=info.get("width", 0) or 0,
                height=info.get("height", 0) or 0,
                fps=float(info.get("fps", 0) or 0),
            )
