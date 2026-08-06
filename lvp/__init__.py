"""
LVP: LLM-Ready Video Package
============================

Edge preprocessing that turns video into a compact keyframe + transcript
package for multimodal LLMs — reducing bandwidth, tokens, and cost while
keeping raw video on-device.

Basic Usage:
    >>> import lvp
    >>> package = lvp.process("video.mp4")
    >>> package.save("video.lvp")

Query-aware / token budget:
    >>> package = lvp.process(
    ...     "video.mp4",
    ...     query="What does the speaker say about inflation?",
    ...     token_budget=8000,
    ... )

Long video chunking:
    >>> result = lvp.process_chunked("long.mp4", chunk_duration=600)
"""

__version__ = "0.2.0"
__author__ = "Girish Sekar"
__license__ = "MIT"

from lvp.core.chunking import ChunkedLVPResult, plan_chunks
from lvp.core.ffmpeg_compat import (
    check_ffmpeg_compatibility,
    get_ffmpeg_version,
    parse_ffmpeg_version,
)
from lvp.core.package import LVPPackage
from lvp.core.processor import DEVICE_PROFILES, LVPProcessor
from lvp.core.reader import LVPReader
from lvp.core.selection import estimate_token_cost, select_by_query


def process(
    video_path: str,
    output: str = None,
    profile: str = "balanced",
    transcribe: bool = True,
    target_keyframes: int = None,
    query: str = None,
    token_budget: int = None,
    **kwargs
) -> 'LVPPackage':
    """
    Process a video and create an LVP package.

    Args:
        video_path: Path to input video file
        output: Optional path for output .lvp file
        profile: Device profile ('minimal', 'balanced', 'quality', 'maximum')
        transcribe: Whether to include speech transcript
        target_keyframes: Override automatic keyframe count
        query: Optional question for query-aware keyframe selection
        token_budget: Optional approximate vision-token budget
        **kwargs: Additional processor options (e.g. scene_threshold)

    Returns:
        LVPPackage object (also saved to disk if output specified)
    """
    processor = LVPProcessor(device_profile=profile)
    package = processor.process(
        video_path,
        include_transcript=transcribe,
        target_keyframes=target_keyframes,
        query=query,
        token_budget=token_budget,
        **kwargs
    )

    if output:
        package.save(output)

    return package


def process_chunked(
    video_path: str,
    chunk_duration: float = 600.0,
    overlap: float = 5.0,
    output_dir: str = None,
    profile: str = "balanced",
    transcribe: bool = True,
    query: str = None,
    token_budget: int = None,
) -> ChunkedLVPResult:
    """Split a long video into overlapping LVP chunks."""
    processor = LVPProcessor(device_profile=profile)
    return processor.process_chunked(
        video_path,
        chunk_duration=chunk_duration,
        overlap=overlap,
        output_dir=output_dir,
        include_transcript=transcribe,
        query=query,
        token_budget=token_budget,
    )


def load(lvp_path: str) -> 'LVPPackage':
    """Load an existing LVP package."""
    return LVPPackage.load(lvp_path)


def get_version():
    """Return the current LVP version."""
    return __version__


__all__ = [
    'DEVICE_PROFILES',
    'ChunkedLVPResult',
    'LVPPackage',
    'LVPProcessor',
    'LVPReader',
    '__version__',
    'check_ffmpeg_compatibility',
    'estimate_token_cost',
    'get_ffmpeg_version',
    'get_version',
    'load',
    'parse_ffmpeg_version',
    'plan_chunks',
    'process',
    'process_chunked',
    'select_by_query',
]
