"""
LLM / VLM service layer.

Encapsulates all calls to OpenAI API for both text (LLM) and
vision (VLM) analysis. All responses are constrained to structured
JSON via Pydantic schemas.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from app.config import get_settings
from app.utils.log import get_logger, log_stage

logger = get_logger("llm")

T = TypeVar("T", bound=BaseModel)


def _get_client():
    """Lazy-initialize OpenAI client."""
    from openai import OpenAI
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. Add it to .env or environment variables."
        )
    return OpenAI(api_key=settings.openai_api_key)


def encode_image_base64(image_path: str) -> str:
    """Read an image file and return base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_llm(
    prompt: str,
    system: str = "You are an expert video content analyst.",
    response_model: Optional[Type[T]] = None,
    model: Optional[str] = None,
) -> T | str:
    """
    Call the LLM with a text prompt.

    If response_model is provided, uses structured output parsing.
    Otherwise returns raw text.
    """
    settings = get_settings()
    client = _get_client()
    model = model or settings.llm_model

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    if response_model is not None:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_model,
            temperature=0.0,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("LLM returned no parsed response")
        return parsed
    else:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
        )
        return completion.choices[0].message.content or ""


def call_vlm(
    image_paths: list[str],
    prompt: str,
    system: str = "You are an expert at detecting advertising content in video frames.",
    response_model: Optional[Type[T]] = None,
    model: Optional[str] = None,
) -> T | str:
    """
    Call the VLM with one or more images and a text prompt.

    Args:
        image_paths: List of local image file paths
        prompt: Text prompt describing what to analyze
        system: System prompt
        response_model: Pydantic model for structured output
        model: Model override

    Returns:
        Parsed response model or raw text
    """
    settings = get_settings()
    client = _get_client()
    model = model or settings.vlm_model

    # Build content with images
    content: list[dict] = []
    for img_path in image_paths:
        b64 = encode_image_base64(img_path)
        ext = Path(img_path).suffix.lstrip(".").lower()
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/{mime};base64,{b64}"},
        })
    content.append({"type": "text", "text": prompt})

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": content},
    ]

    if response_model is not None:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_model,
            temperature=0.0,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("VLM returned no parsed response")
        return parsed
    else:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
        )
        return completion.choices[0].message.content or ""
