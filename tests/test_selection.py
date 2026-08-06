"""Tests for query-aware selection heuristics."""

from lvp.core.selection import (
    estimate_token_cost,
    score_timestamp,
    select_by_query,
    tokenize,
)


def test_tokenize():
    assert "inflation" in tokenize("Why balloons? Inflation!")
    assert "a" not in tokenize("a be cat")  # too short


def test_select_by_token_budget_limits_count():
    candidates = [i * 1.0 for i in range(30)]
    selected = select_by_query(
        candidates=candidates,
        duration=30.0,
        scene_times=[0.0, 10.0, 20.0],
        transcript=None,
        query=None,
        token_budget=5000,
        tokens_per_keyframe=1000,
    )
    assert 1 <= len(selected) <= 5


def test_query_prefers_matching_transcript_region():
    transcript = {
        "full_text": "hello world. later we discuss inflation and balloons.",
        "segments": [
            {"start": 0.0, "end": 2.0, "text": "hello world"},
            {"start": 20.0, "end": 25.0, "text": "inflation and balloons"},
        ],
    }
    candidates = [0.0, 5.0, 10.0, 22.0, 28.0]
    selected = select_by_query(
        candidates=candidates,
        duration=30.0,
        scene_times=[0.0],
        transcript=transcript,
        query="What about inflation?",
        max_keyframes=2,
    )
    assert any(abs(t - 22.0) < 1.0 for t in selected)


def test_score_scene_boundary_bonus():
    s0 = score_timestamp(0.0, set(), None, [0.0, 10.0], 20.0)
    s5 = score_timestamp(5.0, set(), None, [0.0, 10.0], 20.0)
    assert s0 >= s5


def test_estimate_token_cost():
    assert estimate_token_cost(3, transcript_chars=400) >= 3000
