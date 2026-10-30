"""
Local file and direct URL media handling.

Probes media files using FFmpeg to extract metadata without downloading
when the file is already local.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from app.api.schemas import MediaInfo, Platform, VideoKind
from app.utils.log import get_logger, log_stage

logger = get_logger("media")

# Instagram URL pattern (for metadata only — we don't scrape)
_INSTAGRAM_RE = re.compile(r"instagram\.com/(reel|p)/")


def detect_platform(url: str) -> Platform:
    """Detect platform from URL or path."""
    if _INSTAGRAM_RE.search(url):
        return Platform.INSTAGRAM
    parsed = urlparse(url)
    if parsed.scheme in ("", "file") or Path(url).exists():
        return Platform.FILE
    return Platform.OTHER


def probe_media(file_path: str) -> dict:
    """
    Use ffprobe to extract media metadata.

    Returns dict with duration, width, height, fps, etc.
    Raises ValueError on failure.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise ValueError(f"ffprobe failed: {result.stderr[:200]}")
        return json.loads(result.stdout)
    except FileNotFoundError:
        raise ValueError(
            "ffprobe not found. Please install FFmpeg and add it to PATH."
        )


def get_local_media_info(
    file_path: str,
    url: str = "",
    platform: Optional[Platform] = None,
    kind: Optional[VideoKind] = None,
) -> MediaInfo:
    """
    Build MediaInfo from a local file using ffprobe.

    Args:
        file_path: Path to local media file
        url: Original URL if applicable
        platform: Override platform detection
        kind: Override kind detection

    Returns:
        MediaInfo with probed metadata
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Media file not found: {file_path}")

    with log_stage(logger, "probe_media", path=file_path):
        probe = probe_media(file_path)

    # Extract duration
    duration = 0.0
    fmt = probe.get("format", {})
    if "duration" in fmt:
        duration = float(fmt["duration"])

    # Extract video stream info
    width, height, fps = 0, 0, 0.0
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video":
            width = int(stream.get("width", 0))
            height = int(stream.get("height", 0))
            # Parse fps from r_frame_rate (e.g., "30/1")
            rfr = stream.get("r_frame_rate", "0/1")
            if "/" in rfr:
                num, den = rfr.split("/")
                fps = float(num) / float(den) if float(den) > 0 else 0.0
            else:
                fps = float(rfr)
            # Get duration from stream if not in format
            if duration == 0 and "duration" in stream:
                duration = float(stream["duration"])
            break

    # Auto-detect kind if not provided
    if kind is None:
        if duration <= 90:
            kind = VideoKind.SHORT
        else:
            kind = VideoKind.VOD

    if platform is None:
        platform = detect_platform(url or file_path)

    return MediaInfo(
        video_path=str(path.resolve()),
        audio_path=None,
        url=url or str(path),
        platform=platform,
        kind=kind,
        duration_s=duration,
        title=path.stem,
        width=width,
        height=height,
        fps=fps,
    )


def download_direct_url(url: str, output_dir: Optional[str] = None) -> str:
    """
    Download a direct media URL using yt-dlp (handles many formats).

    Returns path to downloaded file.
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
    }

    with log_stage(logger, "download_url", url=url):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise ValueError(f"Failed to download {url}")
            return ydl.prepare_filename(info)
