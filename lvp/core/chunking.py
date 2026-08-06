"""
Long-video chunking: split a source video into time ranges and build
per-chunk LVP packages (or a multi-chunk manifest).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from lvp.core.package import LVPPackage
    from lvp.core.processor import LVPProcessor


@dataclass
class ChunkSpec:
    index: int
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class ChunkedLVPResult:
    """Result of processing a long video as multiple LVP packages."""

    source_path: str
    chunk_duration: float
    overlap: float
    chunks: List[LVPPackage] = field(default_factory=list)
    chunk_specs: List[ChunkSpec] = field(default_factory=list)
    output_paths: List[str] = field(default_factory=list)

    def to_manifest(self) -> Dict[str, Any]:
        return {
            "lvp_chunked_version": "1.0",
            "source": os.path.basename(self.source_path),
            "chunk_duration_seconds": self.chunk_duration,
            "overlap_seconds": self.overlap,
            "chunk_count": len(self.chunks),
            "chunks": [
                {
                    "index": spec.index,
                    "start": spec.start,
                    "end": spec.end,
                    "duration": spec.duration,
                    "package": path,
                    "keyframes": pkg.keyframe_count,
                    "has_transcript": pkg.has_transcript,
                }
                for spec, pkg, path in zip(
                    self.chunk_specs, self.chunks, self.output_paths
                )
            ],
        }

    def save_manifest(self, path: str) -> str:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_manifest(), f, indent=2)
        return path


def plan_chunks(
    duration: float,
    chunk_duration: float = 600.0,
    overlap: float = 5.0,
) -> List[ChunkSpec]:
    """
    Plan [start, end) ranges covering [0, duration].

    For videos shorter than chunk_duration, returns a single chunk.
    """
    if duration <= 0:
        return [ChunkSpec(index=0, start=0.0, end=0.0)]
    if duration <= chunk_duration:
        return [ChunkSpec(index=0, start=0.0, end=duration)]

    step = max(chunk_duration - overlap, 1.0)
    specs: List[ChunkSpec] = []
    start = 0.0
    index = 0
    while start < duration:
        end = min(start + chunk_duration, duration)
        specs.append(ChunkSpec(index=index, start=start, end=end))
        index += 1
        if end >= duration:
            break
        start += step
    return specs


def _cut_segment(
    video_path: str,
    start: float,
    end: float,
    output_path: str,
) -> str:
    """Lossless-ish stream copy cut when possible; re-encode fallback."""
    duration = max(end - start, 0.05)
    cmd = [
        "ffmpeg",
        "-ss",
        str(start),
        "-i",
        video_path,
        "-t",
        str(duration),
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        "-y",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not os.path.exists(output_path):
        # Re-encode fallback for awkward keyframe boundaries
        cmd = [
            "ffmpeg",
            "-ss",
            str(start),
            "-i",
            video_path,
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-y",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to cut segment: {result.stderr}")
    return output_path


def process_chunked(
    processor: LVPProcessor,
    video_path: str,
    chunk_duration: float = 600.0,
    overlap: float = 5.0,
    output_dir: Optional[str] = None,
    include_transcript: bool = True,
    query: Optional[str] = None,
    token_budget: Optional[int] = None,
) -> ChunkedLVPResult:
    """
    Split a long video into overlapping segments and process each with LVP.
    """
    from lvp.core.processor import LVPProcessor  # noqa: F401 — type clarity

    info = processor._get_video_info(video_path)
    duration = float(info["format"]["duration"])
    specs = plan_chunks(duration, chunk_duration=chunk_duration, overlap=overlap)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = tempfile.mkdtemp(prefix="lvp_chunks_")

    result = ChunkedLVPResult(
        source_path=video_path,
        chunk_duration=chunk_duration,
        overlap=overlap,
        chunk_specs=specs,
    )

    base = os.path.splitext(os.path.basename(video_path))[0]

    with tempfile.TemporaryDirectory() as tmp:
        for spec in specs:
            seg_path = os.path.join(tmp, f"chunk_{spec.index:04d}.mp4")
            _cut_segment(video_path, spec.start, spec.end, seg_path)
            package = processor.process(
                seg_path,
                include_transcript=include_transcript,
                query=query,
                token_budget=token_budget,
            )
            # Rewrite source metadata to reflect original timeline
            package.source_filename = (
                f"{base}#chunk{spec.index}[{spec.start:.1f}-{spec.end:.1f}]"
            )
            out_path = os.path.join(output_dir, f"{base}_chunk_{spec.index:04d}.lvp")
            package.save(out_path)
            result.chunks.append(package)
            result.output_paths.append(out_path)

    manifest_path = os.path.join(output_dir, f"{base}_chunks.json")
    result.save_manifest(manifest_path)
    return result
