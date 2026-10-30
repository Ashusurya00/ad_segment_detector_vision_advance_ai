"""
Structured logging for the pipeline.

Each pipeline stage logs: stage name, duration, success/failure,
items processed, model calls, and estimated cost.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(f"ad_detect.{name}")


@contextmanager
def log_stage(
    logger: logging.Logger,
    stage: str,
    **extra: object,
) -> Generator[dict, None, None]:
    """
    Context manager that logs stage entry, timing, and exit.

    Usage:
        with log_stage(logger, "asr") as ctx:
            # do work
            ctx["items"] = 42
    """
    ctx: dict = {"stage": stage, "items": 0, "model_calls": 0, "cost_usd": 0.0}
    ctx.update(extra)
    logger.info("START  %s", stage)
    t0 = time.perf_counter()
    try:
        yield ctx
        elapsed = time.perf_counter() - t0
        logger.info(
            "DONE   %s  elapsed=%.2fs  items=%s  model_calls=%s  cost=$%.4f",
            stage, elapsed, ctx.get("items"), ctx.get("model_calls"), ctx.get("cost_usd", 0),
        )
    except Exception:
        elapsed = time.perf_counter() - t0
        logger.error("FAIL   %s  elapsed=%.2fs", stage, elapsed, exc_info=True)
        raise
