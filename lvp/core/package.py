"""
LVP Package
===========

The LVPPackage class represents a processed video ready for LLM consumption.
"""

import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path


LVP_VERSION = "1.0"


class LVPPackage:
    """
    Represents an LLM-Ready Video Package.
    
    This class holds all the processed video data and can be saved/loaded
    from .lvp files.
    
    Example:
        >>> # Create from processor
        >>> package = processor.process('video.mp4')
        >>> package.save('video.lvp')
        
        >>> # Load existing
        >>> package = LVPPackage.load('video.lvp')
        >>> print(package.transcript)
    """
    
    def __init__(
        self,
        source_filename: str,
        source_duration: float,
        source_resolution: Tuple[int, int],
        source_size: int,
        keyframe_paths: List[str],
        keyframe_timestamps: List[float],
        keyframe_resolution: Tuple[int, int],
        transcript: Optional[Dict[str, Any]] = None,
        scenes: Optional[List[Dict[str, Any]]] = None,
        profile_name: str = "balanced",
        processing_time: float = 0.0,
        _keyframe_data: Optional[List[bytes]] = None,
        _lvp_path: Optional[str] = None
    ):
        """Initialize an LVP package."""
        self.source_filename = source_filename
        self.source_duration = source_duration
        self.source_resolution = source_resolution
        self.source_size = source_size
        self.keyframe_timestamps = keyframe_timestamps
        self.keyframe_resolution = keyframe_resolution
        self.transcript_data = transcript or {
            'segments': [],
            'full_text': '',
            'language': 'unknown'
        }
        self.scenes = scenes or []
        self.profile_name = profile_name
        self.processing_time = processing_time
        self.created_at = datetime.now().isoformat()
        
        # Store keyframe data
        self._keyframe_data = _keyframe_data
        self._keyframe_paths = keyframe_paths
        self._lvp_path = _lvp_path
    
    @property
    def transcript(self) -> str:
        """Get the full transcript text."""
        return self.transcript_data.get('full_text', '')
    
    @property
    def keyframe_count(self) -> int:
        """Get the number of keyframes."""
        return len(self.keyframe_timestamps)
    
    @property
    def scene_count(self) -> int:
        """Get the number of detected scenes."""
        return len(self.scenes)
    
    @property
    def has_transcript(self) -> bool:
        """Check if transcript is available."""
        text = self.transcript_data.get('full_text', '')
        return bool(text and not text.startswith('['))
    
    def get_keyframes(self) -> List[bytes]:
        """
        Get all keyframe images as bytes.
        
        Returns:
            List of image data (WebP format)
        """
        if self._keyframe_data is not None:
            return self._keyframe_data
        
        if self._lvp_path and os.path.exists(self._lvp_path):
            # Load from LVP file
            keyframes = []
            with zipfile.ZipFile(self._lvp_path, 'r') as lvp:
                for name in sorted(lvp.namelist()):
                    if name.startswith('keyframes/') and name.endswith('.webp'):
                        keyframes.append(lvp.read(name))
            return keyframes
        
        if self._keyframe_paths:
            # Load from original paths
            keyframes = []
            for path in self._keyframe_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        keyframes.append(f.read())
            return keyframes
        
        return []
    
    def get_keyframe(self, index: int) -> bytes:
        """Get a specific keyframe by index."""
        keyframes = self.get_keyframes()
        if 0 <= index < len(keyframes):
            return keyframes[index]
        raise IndexError(f"Keyframe index {index} out of range")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the package.
        
        Returns:
            Dictionary with package statistics
        """
        lvp_size = 0
        if self._lvp_path and os.path.exists(self._lvp_path):
            lvp_size = os.path.getsize(self._lvp_path)
        
        return {
            'source_file': self.source_filename,
            'duration_seconds': round(self.source_duration, 2),
            'original_size_mb': round(self.source_size / 1024 / 1024, 2),
            'lvp_size_kb': round(lvp_size / 1024, 2) if lvp_size else 'not saved',
            'compression_ratio': (
                round(self.source_size / lvp_size, 1) 
                if lvp_size else 'not saved'
            ),
            'keyframes': self.keyframe_count,
            'scenes': self.scene_count,
            'has_transcript': self.has_transcript,
            'profile': self.profile_name,
            'processing_time_seconds': round(self.processing_time, 2)
        }
    
    def to_manifest(self) -> Dict[str, Any]:
        """Generate the manifest dictionary."""
        return {
            'lvp_version': LVP_VERSION,
            'created_at': self.created_at,
            'source': {
                'filename': self.source_filename,
                'duration_seconds': self.source_duration,
                'original_resolution': list(self.source_resolution),
                'original_size_bytes': self.source_size
            },
            'processing': {
                'device_profile': self.profile_name,
                'processing_time_seconds': self.processing_time,
                'keyframe_method': 'scene_adaptive',
                'keyframe_timestamps': self.keyframe_timestamps
            },
            'content': {
                'keyframe_count': self.keyframe_count,
                'keyframe_resolution': list(self.keyframe_resolution),
                'has_transcript': self.has_transcript,
                'scene_count': self.scene_count
            }
        }
    
    def to_llm_prompt(self) -> str:
        """
        Convert package to a text prompt for LLMs.
        
        Useful when vision API is not available.
        
        Returns:
            Structured text description of video content
        """
        parts = [
            "# Video Analysis Package",
            f"\n## Source Information",
            f"- File: {self.source_filename}",
            f"- Duration: {self.source_duration:.1f} seconds",
            f"- Resolution: {self.source_resolution[0]}x{self.source_resolution[1]}",
            f"- Keyframes extracted: {self.keyframe_count}",
            f"- Scenes detected: {self.scene_count}",
        ]
        
        if self.has_transcript:
            parts.extend([
                f"\n## Transcript",
                self.transcript
            ])
        
        if self.scenes:
            parts.append("\n## Scene Breakdown")
            for scene in self.scenes:
                duration = scene['end_time'] - scene['start_time']
                parts.append(
                    f"- Scene {scene['scene_id']}: "
                    f"{scene['start_time']:.1f}s - {scene['end_time']:.1f}s "
                    f"({duration:.1f}s, {len(scene['keyframe_indices'])} keyframes)"
                )
        
        return "\n".join(parts)
    
    def save(self, output_path: str) -> str:
        """
        Save the package to an .lvp file.
        
        Args:
            output_path: Path for the output file
            
        Returns:
            Path to saved file
        """
        if not output_path.endswith('.lvp'):
            output_path += '.lvp'
        
        # Get keyframe data
        keyframes = self.get_keyframes()
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as lvp:
            # Write manifest
            manifest = self.to_manifest()
            lvp.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Write keyframes
            for i, kf_data in enumerate(keyframes):
                lvp.writestr(f'keyframes/frame_{i:04d}.webp', kf_data)
            
            # Write transcript
            lvp.writestr(
                'transcript.json', 
                json.dumps(self.transcript_data, indent=2)
            )
            
            # Write scenes
            lvp.writestr(
                'scenes.json',
                json.dumps({'scenes': self.scenes}, indent=2)
            )
        
        self._lvp_path = output_path
        
        # Print summary
        lvp_size = os.path.getsize(output_path)
        compression = self.source_size / lvp_size if lvp_size > 0 else 0
        
        print(f"\n{'='*50}")
        print(f"LVP Package Saved: {output_path}")
        print(f"{'='*50}")
        print(f"Original: {self.source_size / 1024 / 1024:.2f} MB")
        print(f"LVP Size: {lvp_size / 1024:.2f} KB")
        print(f"Compression: {compression:.1f}x")
        print(f"Keyframes: {self.keyframe_count}")
        print(f"{'='*50}\n")
        
        return output_path
    
    @classmethod
    def load(cls, lvp_path: str) -> 'LVPPackage':
        """
        Load a package from an .lvp file.
        
        Args:
            lvp_path: Path to .lvp file
            
        Returns:
            LVPPackage instance
        """
        if not os.path.exists(lvp_path):
            raise FileNotFoundError(f"LVP file not found: {lvp_path}")
        
        with zipfile.ZipFile(lvp_path, 'r') as lvp:
            # Read manifest
            manifest = json.loads(lvp.read('manifest.json'))
            
            # Read transcript
            transcript = json.loads(lvp.read('transcript.json'))
            
            # Read scenes
            scenes_data = json.loads(lvp.read('scenes.json'))
            
            # Read keyframes
            keyframe_data = []
            for name in sorted(lvp.namelist()):
                if name.startswith('keyframes/') and name.endswith('.webp'):
                    keyframe_data.append(lvp.read(name))
        
        source = manifest['source']
        processing = manifest['processing']
        content = manifest['content']
        
        package = cls(
            source_filename=source['filename'],
            source_duration=source['duration_seconds'],
            source_resolution=tuple(source['original_resolution']),
            source_size=source['original_size_bytes'],
            keyframe_paths=[],
            keyframe_timestamps=processing.get('keyframe_timestamps', []),
            keyframe_resolution=tuple(content['keyframe_resolution']),
            transcript=transcript,
            scenes=scenes_data.get('scenes', []),
            profile_name=processing.get('device_profile', 'unknown'),
            processing_time=processing.get('processing_time_seconds', 0),
            _keyframe_data=keyframe_data,
            _lvp_path=lvp_path
        )
        package.created_at = manifest.get('created_at', '')
        
        return package
    
    def __repr__(self) -> str:
        return (
            f"LVPPackage(source='{self.source_filename}', "
            f"duration={self.source_duration:.1f}s, "
            f"keyframes={self.keyframe_count})"
        )
