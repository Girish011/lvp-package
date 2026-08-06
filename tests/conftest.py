"""Shared pytest fixtures — generates a tiny license-clear synthetic video."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_MP4 = FIXTURES / "sample_colorbars.mp4"


def _ensure_sample_video() -> Path:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    if SAMPLE_MP4.exists() and SAMPLE_MP4.stat().st_size > 0:
        return SAMPLE_MP4

    # 3s color bars + sine tone — generated locally, no third-party media license
    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "smptebars=size=320x240:rate=25",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=3",
        "-t",
        "3",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-y",
        str(SAMPLE_MP4),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not SAMPLE_MP4.exists():
        pytest.skip(f"Could not generate fixture video: {result.stderr}")
    return SAMPLE_MP4


@pytest.fixture(scope="session")
def sample_video() -> Path:
    return _ensure_sample_video()


@pytest.fixture(scope="session")
def longer_sample_video(tmp_path_factory) -> Path:
    """~12s clip for chunking tests (chunk_duration=5)."""
    out = tmp_path_factory.mktemp("vid") / "longer.mp4"
    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "smptebars=size=320x240:rate=25",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=880:duration=12",
        "-t",
        "12",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-y",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip(f"Could not generate longer fixture: {result.stderr}")
    return out
