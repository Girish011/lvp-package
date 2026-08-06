"""Unit tests for FFmpeg compatibility helpers."""

from lvp.core.ffmpeg_compat import (
    check_ffmpeg_compatibility,
    fps_mode_flag,
    parse_ffmpeg_version,
)


def test_parse_ffmpeg_version_basic():
    text = "ffmpeg version 8.0.1 Copyright (c) 2000-2025"
    v = parse_ffmpeg_version(text)
    assert v is not None
    assert v.major == 8
    assert v.minor == 0
    assert v.patch == 1
    assert v.at_least(8, 0)


def test_parse_ffmpeg_version_n_prefix():
    text = "ffmpeg version n9.0 Copyright (c) 2000-2026"
    v = parse_ffmpeg_version(text)
    assert v is not None
    assert v.major == 9
    assert v.at_least(9, 0)


def test_fps_mode_flag_not_vsync():
    flags = fps_mode_flag("vfr")
    assert flags == ["-fps_mode", "vfr"]
    assert "-vsync" not in flags


def test_live_ffmpeg_available():
    v = check_ffmpeg_compatibility(warn=False)
    assert v.major >= 4
