"""Tests for long-video chunk planning and processing."""

from lvp import process_chunked
from lvp.core.chunking import plan_chunks


def test_plan_chunks_short_video_single():
    specs = plan_chunks(30.0, chunk_duration=600.0)
    assert len(specs) == 1
    assert specs[0].start == 0.0
    assert specs[0].end == 30.0


def test_plan_chunks_overlap():
    specs = plan_chunks(100.0, chunk_duration=40.0, overlap=5.0)
    assert len(specs) >= 3
    assert specs[0].start == 0.0
    assert specs[-1].end == 100.0
    # Overlap: next start before previous end
    assert specs[1].start < specs[0].end


def test_process_chunked_integration(longer_sample_video, tmp_path):
    out = tmp_path / "chunks"
    result = process_chunked(
        str(longer_sample_video),
        chunk_duration=5.0,
        overlap=1.0,
        output_dir=str(out),
        transcribe=False,
    )
    assert len(result.chunks) >= 2
    assert all(p.endswith(".lvp") for p in result.output_paths)
    manifest = result.to_manifest()
    assert manifest["chunk_count"] == len(result.chunks)
