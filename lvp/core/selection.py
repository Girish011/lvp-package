"""
Query-aware and token-budget keyframe selection.

Scores candidate timestamps using transcript keyword overlap with the query
and scene-boundary priority. Optional embedding scoring when
`sentence-transformers` is installed.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from typing import Any, Dict, List, Optional, Set

_WORD_RE = re.compile(r"[a-z0-9']+", re.IGNORECASE)


_STOPWORDS = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "have", "been", "what", "when",
    "where", "which", "who", "whom", "this", "that", "with", "from", "about",
    "into", "does", "did", "how", "why", "any", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "just", "also",
})


def tokenize(text: str) -> Set[str]:
    """Lowercase alphanumeric tokens, dropping stopwords and tiny tokens."""
    return {
        t
        for t in _WORD_RE.findall(text.lower())
        if len(t) > 2 and t not in _STOPWORDS
    }


def _segment_text_at(
    transcript: Optional[Dict[str, Any]],
    timestamp: float,
    window: float = 5.0,
) -> str:
    """Return transcript text near timestamp only (no full-text fallback)."""
    if not transcript:
        return ""
    parts: List[str] = []
    for seg in transcript.get("segments", []):
        start = float(seg.get("start", 0))
        end = float(seg.get("end", start))
        if end < timestamp - window or start > timestamp + window:
            continue
        parts.append(str(seg.get("text", "")))
    return " ".join(parts)


def score_timestamp(
    timestamp: float,
    query_tokens: Set[str],
    transcript: Optional[Dict[str, Any]],
    scene_times: Sequence[float],
    duration: float,
) -> float:
    """
    Heuristic score:
    - strong keyword overlap with nearby transcript (query-aware)
    - weaker full-transcript presence signal
    - scene boundary bonus (secondary when a query is set)
    """
    score = 0.0
    local = tokenize(_segment_text_at(transcript, timestamp))
    if query_tokens and local:
        overlap = len(query_tokens & local) / max(len(query_tokens), 1)
        score += 3.0 * overlap
    if query_tokens and transcript:
        full = tokenize(str(transcript.get("full_text", "")))
        # Tiny global prior so videos with any match beat pure silence
        score += 0.05 * (len(query_tokens & full) / max(len(query_tokens), 1))

    # Scene boundary proximity (keep weaker than a real keyword hit)
    scene_weight = 0.35 if query_tokens else 0.75
    if scene_times:
        dist = min(abs(timestamp - s) for s in scene_times)
        if dist < 0.25:
            score += scene_weight
        elif dist < 1.0:
            score += scene_weight * 0.35

    # Slight mid-video prior for empty queries
    if not query_tokens and duration > 0:
        mid = abs(timestamp - duration / 2) / duration
        score += 0.15 * (1.0 - mid)

    return score


def select_by_query(
    candidates: Sequence[float],
    duration: float,
    scene_times: Sequence[float],
    transcript: Optional[Dict[str, Any]],
    query: Optional[str],
    token_budget: Optional[int] = None,
    max_keyframes: Optional[int] = None,
    tokens_per_keyframe: int = 1000,
) -> List[float]:
    """
    Rank candidate timestamps by query relevance under a keyframe/token budget.

    Args:
        candidates: Candidate timestamps (usually scene + uniform samples)
        duration: Video duration seconds
        scene_times: Detected scene boundaries
        transcript: Whisper-style transcript dict
        query: User question (None → fall back to even coverage ranking)
        token_budget: Approximate vision-token budget (maps to max keyframes)
        max_keyframes: Hard cap on selected frames
        tokens_per_keyframe: Rough token cost estimate per image
    """
    if not candidates:
        return [0.0]

    limit = max_keyframes
    if token_budget is not None:
        budget_limit = max(1, token_budget // max(tokens_per_keyframe, 1))
        limit = budget_limit if limit is None else min(limit, budget_limit)
    if limit is None:
        limit = len(candidates)
    limit = max(1, min(limit, len(candidates)))

    query_tokens = tokenize(query or "")

    scored = [
        (
            score_timestamp(ts, query_tokens, transcript, scene_times, duration),
            ts,
        )
        for ts in candidates
    ]
    scored.sort(key=lambda x: (-x[0], x[1]))

    # Greedy diversity: pick highest score with minimum temporal gap
    min_gap = duration / (limit * 2) if duration > 0 and limit > 0 else 0.5
    selected: List[float] = []
    for _, ts in scored:
        if any(abs(ts - s) < min_gap for s in selected):
            continue
        selected.append(ts)
        if len(selected) >= limit:
            break

    # Always ensure first frame if budget allows and video has content
    if 0.0 not in selected and len(selected) < limit:
        selected.append(0.0)
    elif 0.0 not in selected and selected:
        # Replace lowest-priority (last appended among weak scores) only if empty query
        if not query_tokens:
            selected[-1] = 0.0

    # Fill remaining with evenly spaced picks if under budget
    if len(selected) < limit:
        for i in range(limit):
            ts = (i / max(limit - 1, 1)) * max(duration - 0.01, 0)
            if any(abs(ts - s) < min_gap for s in selected):
                continue
            selected.append(ts)
            if len(selected) >= limit:
                break

    return sorted(set(round(t, 3) for t in selected))[:limit]


def estimate_token_cost(
    keyframe_count: int,
    transcript_chars: int = 0,
    tokens_per_keyframe: int = 1000,
    chars_per_token: float = 4.0,
) -> int:
    """Rough multimodal token estimate for budgeting."""
    text_tokens = int(math.ceil(transcript_chars / chars_per_token)) if transcript_chars else 0
    return keyframe_count * tokens_per_keyframe + text_tokens
