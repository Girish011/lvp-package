"""
LVP Core Processor
==================

Main processing pipeline for creating LVP packages from video files.
"""

import os
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, asdict

from lvp.core.package import LVPPackage


@dataclass
class DeviceProfile:
    """Configuration for different device capabilities."""
    name: str
    keyframes_per_minute: int
    resolution: Tuple[int, int]
    quality: int  # WebP quality 1-100
    transcription_model: str
    max_processing_time_ratio: float  # seconds per second of video


# Predefined profiles
DEVICE_PROFILES = {
    'minimal': DeviceProfile(
        name='minimal',
        keyframes_per_minute=6,
        resolution=(384, 216),
        quality=60,
        transcription_model='tiny',
        max_processing_time_ratio=0.1
    ),
    'balanced': DeviceProfile(
        name='balanced',
        keyframes_per_minute=12,
        resolution=(512, 288),
        quality=75,
        transcription_model='base',
        max_processing_time_ratio=0.2
    ),
    'quality': DeviceProfile(
        name='quality',
        keyframes_per_minute=20,
        resolution=(640, 360),
        quality=85,
        transcription_model='small',
        max_processing_time_ratio=0.4
    ),
    'maximum': DeviceProfile(
        name='maximum',
        keyframes_per_minute=30,
        resolution=(854, 480),
        quality=90,
        transcription_model='medium',
        max_processing_time_ratio=0.6
    ),
}


class LVPProcessor:
    """
    Main processor for creating LVP packages from videos.
    
    Example:
        >>> processor = LVPProcessor(device_profile='balanced')
        >>> package = processor.process('video.mp4')
        >>> package.save('video.lvp')
    """
    
    def __init__(self, device_profile: str = 'balanced'):
        """
        Initialize the LVP processor.
        
        Args:
            device_profile: One of 'minimal', 'balanced', 'quality', 'maximum'
        """
        if device_profile not in DEVICE_PROFILES:
            raise ValueError(
                f"Unknown profile '{device_profile}'. "
                f"Choose from: {list(DEVICE_PROFILES.keys())}"
            )
        self.profile = DEVICE_PROFILES[device_profile]
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Verify required tools are available."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg: "
                "https://ffmpeg.org/download.html"
            )
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to read video: {result.stderr}")
        return json.loads(result.stdout)
    
    def _detect_scenes(
        self, 
        video_path: str, 
        threshold: float = 0.3
    ) -> List[float]:
        """
        Detect scene changes using FFmpeg's scene filter.
        
        Returns list of timestamps where scenes change.
        """
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', f'select=gt(scene\\,{threshold}),showinfo',
            '-f', 'null', '-'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        scene_times = [0.0]
        for line in result.stderr.split('\n'):
            if 'pts_time:' in line:
                try:
                    pts_part = line.split('pts_time:')[1].split()[0]
                    scene_times.append(float(pts_part))
                except (IndexError, ValueError):
                    continue
        
        return sorted(set(scene_times))
    
    def _select_keyframe_timestamps(
        self,
        duration: float,
        scene_times: List[float],
        target_count: Optional[int] = None
    ) -> List[float]:
        """
        Select keyframe timestamps using adaptive algorithm.
        
        Strategy:
        1. Always include scene boundaries
        2. Fill gaps with uniform sampling
        3. Ensure minimum temporal spacing
        """
        if target_count is None:
            target_count = max(
                1, 
                int(duration / 60 * self.profile.keyframes_per_minute)
            )
        
        min_gap = duration / (target_count * 2) if target_count > 0 else 1.0
        
        # Start with scene boundaries
        selected = set(scene_times)
        
        # Add uniformly spaced frames
        if target_count > 0:
            uniform_interval = duration / target_count
            for i in range(target_count):
                ts = i * uniform_interval
                too_close = any(abs(ts - s) < min_gap for s in selected)
                if not too_close:
                    selected.add(ts)
        
        # Limit total count
        selected = sorted(selected)
        if len(selected) > target_count * 1.5:
            scene_set = set(scene_times)
            non_scene = [t for t in selected if t not in scene_set]
            keep_count = max(0, target_count - len(scene_times))
            if keep_count > 0 and len(non_scene) > keep_count:
                step = max(1, len(non_scene) // keep_count)
                non_scene = non_scene[::step][:keep_count]
            selected = sorted(set(scene_times) | set(non_scene))
        
        return selected
    
    def _extract_keyframes(
        self,
        video_path: str,
        timestamps: List[float],
        output_dir: str
    ) -> List[str]:
        """Extract keyframes at specified timestamps as WebP images."""
        keyframe_paths = []
        w, h = self.profile.resolution
        
        for i, ts in enumerate(timestamps):
            output_path = os.path.join(output_dir, f'frame_{i:04d}.webp')
            cmd = [
                'ffmpeg', '-ss', str(ts), '-i', video_path,
                '-vframes', '1',
                '-vf', f'scale={w}:{h}',
                '-quality', str(self.profile.quality),
                '-y', output_path
            ]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0 and os.path.exists(output_path):
                keyframe_paths.append(output_path)
        
        return keyframe_paths
    
    def _extract_transcript(
        self,
        video_path: str,
        output_dir: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract audio and generate transcript.
        
        Note: Full implementation requires Whisper.
        This version creates a placeholder or uses system ASR.
        """
        audio_path = os.path.join(output_dir, 'audio.wav')
        
        # Extract audio
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1',
            '-y', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0 or not os.path.exists(audio_path):
            return None
        
        # Check if whisper is available
        try:
            import whisper
            model = whisper.load_model(self.profile.transcription_model)
            result = model.transcribe(audio_path)
            
            segments = [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip(),
                    'confidence': seg.get('confidence', 1.0),
                    'aligned_keyframes': []
                }
                for seg in result.get('segments', [])
            ]
            
            return {
                'segments': segments,
                'full_text': result.get('text', '').strip(),
                'language': result.get('language', 'en')
            }
            
        except ImportError:
            # Whisper not installed - return placeholder
            return {
                'segments': [{
                    'start': 0.0,
                    'end': 0.0,
                    'text': '[Whisper not installed - run: pip install openai-whisper]',
                    'confidence': 0.0,
                    'aligned_keyframes': []
                }],
                'full_text': '[Whisper not installed]',
                'language': 'unknown'
            }
    
    def process(
        self,
        video_path: str,
        include_transcript: bool = True,
        target_keyframes: Optional[int] = None,
        scene_threshold: float = 0.3
    ) -> 'LVPPackage':
        """
        Process a video and create an LVP package.
        
        Args:
            video_path: Path to input video
            include_transcript: Whether to include speech transcript
            target_keyframes: Override automatic keyframe count
            scene_threshold: Sensitivity for scene detection (0-1)
            
        Returns:
            LVPPackage object
        """
        start_time = datetime.now()
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        # Get video info
        video_info = self._get_video_info(video_path)
        video_stream = next(
            (s for s in video_info['streams'] if s['codec_type'] == 'video'),
            None
        )
        if video_stream is None:
            raise ValueError("No video stream found in file")
        
        duration = float(video_info['format']['duration'])
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        source_size = os.path.getsize(video_path)
        
        # Process in temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            keyframes_dir = os.path.join(temp_dir, 'keyframes')
            os.makedirs(keyframes_dir)
            
            # Detect scenes
            scene_times = self._detect_scenes(video_path, scene_threshold)
            
            # Select keyframes
            timestamps = self._select_keyframe_timestamps(
                duration, scene_times, target_keyframes
            )
            
            # Extract keyframes
            keyframe_paths = self._extract_keyframes(
                video_path, timestamps, keyframes_dir
            )
            
            # Extract transcript
            transcript_data = None
            if include_transcript:
                transcript_data = self._extract_transcript(video_path, temp_dir)
            
            # Build scene info
            scenes = []
            for i, (start, end) in enumerate(
                zip(scene_times, scene_times[1:] + [duration])
            ):
                scene_keyframes = [
                    j for j, ts in enumerate(timestamps)
                    if start <= ts < end
                ]
                scenes.append({
                    'scene_id': i,
                    'start_time': start,
                    'end_time': end,
                    'keyframe_indices': scene_keyframes
                })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Read keyframe data into memory BEFORE temp dir is cleaned up
            keyframe_data = []
            for kf_path in keyframe_paths:
                if os.path.exists(kf_path):
                    with open(kf_path, 'rb') as f:
                        keyframe_data.append(f.read())
            
            # Create package with keyframe data in memory
            package = LVPPackage(
                source_filename=os.path.basename(video_path),
                source_duration=duration,
                source_resolution=(width, height),
                source_size=source_size,
                keyframe_paths=[],  # Paths no longer valid after temp cleanup
                keyframe_timestamps=timestamps,
                keyframe_resolution=self.profile.resolution,
                transcript=transcript_data,
                scenes=scenes,
                profile_name=self.profile.name,
                processing_time=processing_time,
                _keyframe_data=keyframe_data  # Store actual data
            )
            
            return package
