"""
Time formatting and conversion utilities.
"""

from __future__ import annotations


def seconds_to_mmss(s: float) -> str:
    """Convert seconds to MM:SS.f format."""
    mins = int(s // 60)
    secs = s % 60
    return f"{mins:02d}:{secs:05.2f}"


def seconds_to_hhmmss(s: float) -> str:
    """Convert seconds to HH:MM:SS.f format."""
    hrs = int(s // 3600)
    remainder = s % 3600
    mins = int(remainder // 60)
    secs = remainder % 60
    return f"{hrs:02d}:{mins:02d}:{secs:05.2f}"


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value between lo and hi."""
    return max(lo, min(hi, value))
