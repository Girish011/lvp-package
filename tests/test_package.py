"""Package helper unit tests without video."""

from lvp.core.package import LVPPackage


def test_to_llm_prompt_and_manifest():
    pkg = LVPPackage(
        source_filename="x.mp4",
        source_duration=10.0,
        source_resolution=(640, 480),
        source_size=1_000_000,
        keyframe_paths=[],
        keyframe_timestamps=[0.0, 5.0],
        keyframe_resolution=(512, 288),
        transcript={"full_text": "hello", "segments": [], "language": "en"},
        scenes=[{
            "scene_id": 0,
            "start_time": 0.0,
            "end_time": 10.0,
            "keyframe_indices": [0, 1],
        }],
        keyframe_method="scene_adaptive",
        _keyframe_data=[b"fakewebp0", b"fakewebp1"],
    )
    prompt = pkg.to_llm_prompt()
    assert "hello" in prompt
    assert "Keyframes extracted: 2" in prompt
    manifest = pkg.to_manifest()
    assert manifest["lvp_version"] == "1.0"
    assert manifest["content"]["keyframe_count"] == 2
    assert pkg.has_transcript is True
