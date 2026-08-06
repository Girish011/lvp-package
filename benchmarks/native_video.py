"""
Native video API comparison stubs.

Implement provider-specific uploads here for fair LVP vs native evals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def query_gemini_native_video(
    video_path: Path, question: str, api_key: str | None = None
) -> dict[str, Any]:
    """
    Upload raw video via Gemini Files API and ask `question`.

    Returns a result dict; raises ImportError / NotImplementedError until wired.
    """
    raise NotImplementedError(
        "Implement Gemini Files API upload for native-video baseline. "
        "See https://ai.google.dev/gemini-api/docs/vision"
    )


def query_claude_native_video(
    video_path: Path, question: str, api_key: str | None = None
) -> dict[str, Any]:
    """Upload/attach raw video for Claude video (when available in your API tier)."""
    raise NotImplementedError(
        "Implement Claude native video input for baseline comparisons."
    )
