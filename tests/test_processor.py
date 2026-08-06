"""Integration tests for processor and package I/O."""

import zipfile

import lvp
from lvp import LVPProcessor


def test_process_and_roundtrip(sample_video, tmp_path):
    out = tmp_path / "sample.lvp"
    package = lvp.process(
        str(sample_video),
        output=str(out),
        profile="minimal",
        transcribe=False,
    )
    assert out.exists()
    assert package.keyframe_count >= 1
    assert package.ffmpeg_version

    loaded = lvp.load(str(out))
    assert loaded.keyframe_count == package.keyframe_count
    assert len(loaded.get_keyframes()) == loaded.keyframe_count
    summary = loaded.summary()
    assert summary["keyframes"] >= 1
    assert isinstance(summary["compression_ratio"], (int, float))

    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        assert "manifest.json" in names
        assert "scenes.json" in names
        assert any(n.startswith("keyframes/") for n in names)


def test_query_aware_process(sample_video, tmp_path):
    package = lvp.process(
        str(sample_video),
        profile="minimal",
        transcribe=False,
        query="What colors are on the bars?",
        token_budget=4000,
        target_keyframes=3,
    )
    assert package.keyframe_method in ("query_aware", "token_budget")
    assert package.keyframe_count <= 3
    out = tmp_path / "q.lvp"
    package.save(str(out))
    loaded = lvp.load(str(out))
    assert loaded.query == package.query


def test_invalid_profile():
    try:
        LVPProcessor(device_profile="nope")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_version():
    assert lvp.get_version() == "0.2.0"
