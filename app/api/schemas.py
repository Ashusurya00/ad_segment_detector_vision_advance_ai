"""
Pydantic schemas for the ad detection API.

These models define the required API input/output contract exactly as specified
in the assignment. Extra fields are allowed where useful.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────

class Platform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FILE = "file"
    OTHER = "other"


class VideoKind(str, Enum):
    VOD = "vod"
    SHORT = "short"
    LIVE = "live"


class AdType(str, Enum):
    PREROLL = "preroll"
    MIDROLL_SPONSOR_READ = "midroll_sponsor_read"
    PRODUCT_PLACEMENT = "product_placement"
    SELF_PROMO = "self_promo"
    AFFILIATE = "affiliate"
    PLATFORM_INSERTED = "platform_inserted"
    BUMPER = "bumper"
    OTHER = "other"


# ── Request ────────────────────────────────────────────────────────────────

class DetectionOptions(BaseModel):
    """Optional processing overrides."""
    fps_override: Optional[float] = None
    confidence_threshold: Optional[float] = None
    max_vlm_calls: Optional[int] = None
    skip_ocr: bool = False
    skip_vlm: bool = False


class DetectionRequest(BaseModel):
    """POST /detect request body."""
    url: str = Field(..., description="Video URL or local file path")
    kind: Optional[VideoKind] = Field(None, description="auto-detected if omitted")
    options: Optional[DetectionOptions] = None


# ── Response ───────────────────────────────────────────────────────────────

class SourceInfo(BaseModel):
    url: str
    platform: Platform
    kind: VideoKind
    duration_s: float
    processed_at: datetime


class Evidence(BaseModel):
    frame_timestamps: list[float] = Field(default_factory=list)
    transcript_span: Optional[str] = None
    ocr_text: list[str] = Field(default_factory=list)
    detected_brand: Optional[str] = None
    signals_used: list[str] = Field(default_factory=list)
    model_reasoning: Optional[str] = None


class AdSegment(BaseModel):
    id: str
    start_s: float
    end_s: float
    ad_type: AdType
    confidence: float
    brand: Optional[str] = None
    description: str
    evidence: Evidence


class ProcessingStats(BaseModel):
    wall_clock_s: float
    estimated_cost_usd: float
    frames_sampled: int
    model_calls: int
    realtime_factor: Optional[float] = None


class DetectionResponse(BaseModel):
    source: SourceInfo
    segments: list[AdSegment]
    stats: ProcessingStats


# ── Internal data models (not part of API contract) ────────────────────────

class TranscriptSegment(BaseModel):
    """A chunk of ASR transcript with timing."""
    text: str
    start_s: float
    end_s: float
    words: list[dict] = Field(default_factory=list)  # [{word, start, end}]


class FrameInfo(BaseModel):
    """Metadata for a sampled frame."""
    timestamp_s: float
    frame_index: int
    path: str  # path to saved frame image


class SignalHit(BaseModel):
    """A detected advertising signal at a point or span in time."""
    signal_type: str      # "asr", "ocr", "vlm_frame", "scene_cut"
    start_s: float
    end_s: float
    score: float          # 0-1 strength of this signal
    details: dict = Field(default_factory=dict)  # signal-specific payload


class CandidateRegion(BaseModel):
    """A candidate ad region before final segmentation."""
    start_s: float
    end_s: float
    signals: list[SignalHit] = Field(default_factory=list)
    ad_type: Optional[AdType] = None
    brand: Optional[str] = None
    description: str = ""
    raw_confidence: float = 0.0


class MediaInfo(BaseModel):
    """Information about ingested media."""
    video_path: str
    audio_path: Optional[str] = None
    url: str
    platform: Platform
    kind: VideoKind
    duration_s: float
    title: str = ""
    width: int = 0
    height: int = 0
    fps: float = 0.0


class CostTracker(BaseModel):
    """Tracks API costs and resource usage during a pipeline run."""
    vlm_calls: int = 0
    llm_calls: int = 0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    frames_sampled: int = 0
    whisper_duration_s: float = 0.0

    def total_model_calls(self) -> int:
        return self.vlm_calls + self.llm_calls

    def estimated_cost(self, settings) -> float:
        """Calculate estimated USD cost."""
        vlm_cost = self.vlm_calls * settings.vlm_cost_per_call
        llm_cost = (self.llm_input_tokens / 1000) * settings.llm_cost_per_1k_tokens
        return round(vlm_cost + llm_cost, 4)
