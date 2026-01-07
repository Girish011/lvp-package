"""
LVP: LLM-Ready Video Package
============================

A universal standard for bandwidth-efficient video upload to multimodal LLMs.

Basic Usage:
    >>> import lvp
    >>> package = lvp.process("video.mp4")
    >>> package.save("video.lvp")
    
    >>> # Or one-liner
    >>> lvp.process("video.mp4", output="video.lvp")

With Options:
    >>> package = lvp.process(
    ...     "video.mp4",
    ...     profile="balanced",      # minimal, balanced, quality, maximum
    ...     transcribe=True,         # Include speech transcript
    ...     target_keyframes=20,     # Override auto-selection
    ... )

Reading LVP Files:
    >>> package = lvp.load("video.lvp")
    >>> print(package.summary())
    >>> print(package.transcript)
    >>> keyframes = package.get_keyframes()

Cross-Provider Queries:
    >>> from lvp.providers import ClaudeProvider
    >>> claude = ClaudeProvider(api_key="...")
    >>> response = claude.query(package, "What happens in this video?")
"""

__version__ = "0.1.0"
__author__ = "LVP Research Partnership"
__license__ = "MIT"

from lvp.core.processor import LVPProcessor
from lvp.core.reader import LVPReader
from lvp.core.package import LVPPackage

# Convenience functions
def process(
    video_path: str,
    output: str = None,
    profile: str = "balanced",
    transcribe: bool = True,
    target_keyframes: int = None,
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
        **kwargs: Additional processor options
        
    Returns:
        LVPPackage object (also saved to disk if output specified)
        
    Example:
        >>> package = lvp.process("my_video.mp4")
        >>> package.save("my_video.lvp")
    """
    processor = LVPProcessor(device_profile=profile)
    package = processor.process(
        video_path,
        include_transcript=transcribe,
        target_keyframes=target_keyframes,
        **kwargs
    )
    
    if output:
        package.save(output)
    
    return package


def load(lvp_path: str) -> 'LVPPackage':
    """
    Load an existing LVP package.
    
    Args:
        lvp_path: Path to .lvp file
        
    Returns:
        LVPPackage object
        
    Example:
        >>> package = lvp.load("my_video.lvp")
        >>> print(package.transcript)
    """
    return LVPPackage.load(lvp_path)


# Version info
def get_version():
    """Return the current LVP version."""
    return __version__


__all__ = [
    'process',
    'load',
    'get_version',
    'LVPProcessor',
    'LVPReader', 
    'LVPPackage',
    '__version__',
]
