"""
FFmpeg compatibility helpers for LVP.

Supports FFmpeg 8.x and 9.0+. Never use the removed `-vsync` flag;
prefer `-fps_mode` when frame timing must be set explicitly.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple

MIN_RECOMMENDED = (8, 0)
PREFERRED = (9, 0)


@dataclass(frozen=True)
class FFmpegVersion:
    major: int
    minor: int
    patch: int
    raw: str

    @property
    def tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def at_least(self, major: int, minor: int = 0, patch: int = 0) -> bool:
        return self.tuple >= (major, minor, patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def parse_ffmpeg_version(version_text: str) -> Optional[FFmpegVersion]:
    """Parse `ffmpeg -version` stdout into a structured version."""
    match = re.search(
        r"ffmpeg version\s+(\d+)\.(\d+)(?:\.(\d+))?",
        version_text,
        re.IGNORECASE,
    )
    if not match:
        # Some builds: "ffmpeg version n8.0.1" or "ffmpeg version 8.0"
        match = re.search(
            r"ffmpeg version\s+n?(\d+)\.(\d+)(?:\.(\d+))?",
            version_text,
            re.IGNORECASE,
        )
    if not match:
        return None
    major, minor = int(match.group(1)), int(match.group(2))
    patch = int(match.group(3) or 0)
    return FFmpegVersion(major=major, minor=minor, patch=patch, raw=match.group(0))


def get_ffmpeg_version(ffmpeg_bin: str = "ffmpeg") -> FFmpegVersion:
    """Run ffmpeg and return parsed version. Raises RuntimeError if missing."""
    try:
        result = subprocess.run(
            [ffmpeg_bin, "-version"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError(
            "FFmpeg not found. Install FFmpeg 8.0+: https://ffmpeg.org/download.html"
        ) from exc

    parsed = parse_ffmpeg_version(result.stdout or result.stderr)
    if parsed is None:
        raise RuntimeError(
            "Could not parse FFmpeg version from `ffmpeg -version` output."
        )
    return parsed


def check_ffmpeg_compatibility(
    ffmpeg_bin: str = "ffmpeg",
    warn: bool = True,
) -> FFmpegVersion:
    """
    Verify FFmpeg is available and warn if below recommended major version.

    LVP is tested against FFmpeg 8.x and 9.0. Older majors may still work
    for basic scene detect + frame extract, but are unsupported.
    """
    version = get_ffmpeg_version(ffmpeg_bin)
    if warn and not version.at_least(*MIN_RECOMMENDED):
        import warnings

        warnings.warn(
            f"FFmpeg {version} detected; LVP recommends >= {MIN_RECOMMENDED[0]}.{MIN_RECOMMENDED[1]}. "
            f"Prefer FFmpeg {PREFERRED[0]}.{PREFERRED[1]}+ when available.",
            UserWarning,
            stacklevel=2,
        )
    return version


def fps_mode_flag(mode: str = "vfr") -> list:
    """
    Return CLI args for frame timing.

    FFmpeg 9.0 removed `-vsync`; use `-fps_mode` instead.
    """
    return ["-fps_mode", mode]


def has_whisper_filter(ffmpeg_bin: str = "ffmpeg") -> bool:
    """Return True if this FFmpeg build exposes the whisper filter (8.0+ family)."""
    try:
        result = subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-filters"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return re.search(r"\bwhisper\b", result.stdout) is not None


def has_onnx_dnn(ffmpeg_bin: str = "ffmpeg") -> bool:
    """Return True if FFmpeg reports ONNX/DNN backend support (9.0 opportunity)."""
    try:
        result = subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-filters"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    text = result.stdout.lower()
    return "dnn" in text or "onnx" in text
