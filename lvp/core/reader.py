"""
LVP Reader
==========

Legacy reader class - now uses LVPPackage.load()
Kept for backwards compatibility.
"""

from lvp.core.package import LVPPackage


class LVPReader:
    """
    Reader for LVP packages.
    
    Note: This is a legacy class. Use LVPPackage.load() directly.
    
    Example:
        >>> reader = LVPReader('video.lvp')
        >>> print(reader.get_transcript_text())
    """
    
    def __init__(self, lvp_path: str):
        """Load an LVP package."""
        self._package = LVPPackage.load(lvp_path)
    
    @property
    def manifest(self):
        return self._package.to_manifest()
    
    @property
    def transcript(self):
        return self._package.transcript_data
    
    @property
    def scenes(self):
        return {'scenes': self._package.scenes}
    
    def get_keyframe(self, index: int) -> bytes:
        return self._package.get_keyframe(index)
    
    def get_all_keyframes(self):
        return self._package.get_keyframes()
    
    def get_transcript_text(self) -> str:
        return self._package.transcript
    
    def to_llm_prompt(self) -> str:
        return self._package.to_llm_prompt()
    
    def summary(self):
        return self._package.summary()
