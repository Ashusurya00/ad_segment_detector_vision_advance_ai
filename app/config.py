"""
Centralized configuration for the ad segment detection pipeline.

All tuneable parameters live here. Override via environment variables or .env file.
No magic numbers should exist elsewhere in the codebase.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Pipeline configuration — override any value via environment variable."""

    # ── Paths ──────────────────────────────────────────────────────────
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )
    output_dir: str = "outputs"

    # ── API Keys ───────────────────────────────────────────────────────
    openai_api_key: str = ""

    # ── Models ─────────────────────────────────────────────────────────
    whisper_model: str = "base"          # tiny | base | small | medium | large
    vlm_model: str = "gpt-4o-mini"       # vision-capable model for frame analysis
    llm_model: str = "gpt-4o-mini"       # text model for transcript classification

    # ── Sampling rates (frames per second) ─────────────────────────────
    long_form_fps: float = 0.2           # baseline for long-form (1 frame / 5 s)
    short_video_fps: float = 1.0         # uniform for short-form
    candidate_boost_fps: float = 2.0     # boosted around ASR-flagged regions
    bumper_fps: float = 4.0              # dense sampling for bumper detection
    candidate_window_pad_s: float = 10.0 # seconds of padding around ASR candidates

    # ── Segmentation ───────────────────────────────────────────────────
    merge_gap_s: float = 3.0             # merge segments within this gap
    min_segment_duration_s: float = 0.5  # discard segments shorter than this
    max_segment_gap_for_split_s: float = 5.0  # split threshold for distinct ads

    # ── Confidence weights (must sum to 1.0) ───────────────────────────
    w_asr: float = 0.35
    w_ocr: float = 0.15
    w_visual: float = 0.20
    w_temporal: float = 0.15
    w_phrase: float = 0.15

    # ── Thresholds ─────────────────────────────────────────────────────
    confidence_threshold: float = 0.30   # minimum to report a segment
    scene_detection_threshold: float = 27.0  # PySceneDetect content threshold

    # ── Limits ─────────────────────────────────────────────────────────
    max_video_duration_s: float = 7200.0  # 2 hours
    max_vlm_calls_per_video: int = 30     # cost cap on vision API calls
    max_file_size_mb: float = 2000.0      # 2 GB

    # ── Live stream ────────────────────────────────────────────────────
    live_window_s: float = 60.0
    live_overlap_s: float = 10.0

    # ── Cost estimates (USD) ───────────────────────────────────────────
    vlm_cost_per_call: float = 0.002     # GPT-4o-mini with image
    llm_cost_per_1k_tokens: float = 0.00015  # GPT-4o-mini input
    whisper_local: bool = True            # True = free local, False = API

    # ── ASR sponsor phrases ────────────────────────────────────────────
    sponsor_phrases: list[str] = Field(default=[
        "sponsored by", "brought to you by", "this video is sponsored",
        "thanks to", "use code", "use my code", "discount code",
        "promo code", "coupon code", "link in description",
        "link in the description", "link in bio", "check out",
        "go to", "visit", "sign up", "free trial", "percent off",
        "% off", "dollars off", "special offer", "limited time",
        "affiliate", "partner", "partnership",
    ])

    self_promo_phrases: list[str] = Field(default=[
        "subscribe", "hit the bell", "like and subscribe",
        "join my patreon", "my merch", "my store", "my website",
        "follow me on", "second channel",
    ])

    # ── OCR ad indicators ──────────────────────────────────────────────
    ocr_ad_patterns: list[str] = Field(default=[
        "sponsored", "ad", "advertisement", "promo", "discount",
        "% off", "use code", "free trial", "shop now", "buy now",
        "limited time", "special offer", "click link",
    ])

    # ── Determinism ────────────────────────────────────────────────────
    random_seed: int = 42

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()
