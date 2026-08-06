#!/usr/bin/env python3
"""
LVP comparison harness: packaging metrics + optional provider queries.

Examples:
  python benchmarks/run_comparison.py --video clip.mp4 --dry-run
  python benchmarks/run_comparison.py --video clip.mp4 --providers openai --questions "What happens?"
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_QUESTIONS = [
    "What is happening in this video?",
    "Describe the main objects or people visible.",
    "What is the setting or environment?",
    "Summarize this video in one sentence.",
]


def package_metrics(video: Path, profile: str, transcribe: bool, query: Optional[str], token_budget: Optional[int]) -> Dict[str, Any]:
    import lvp

    t0 = time.perf_counter()
    package = lvp.process(
        str(video),
        profile=profile,
        transcribe=transcribe,
        query=query,
        token_budget=token_budget,
    )
    pack_ms = (time.perf_counter() - t0) * 1000

    tmp = video.with_suffix(".bench.lvp")
    package.save(str(tmp))
    lvp_bytes = tmp.stat().st_size
    try:
        tmp.unlink()
    except OSError:
        pass

    original = video.stat().st_size
    return {
        "source": video.name,
        "original_bytes": original,
        "lvp_bytes": lvp_bytes,
        "compression_ratio": round(original / lvp_bytes, 2) if lvp_bytes else None,
        "keyframes": package.keyframe_count,
        "scenes": package.scene_count,
        "has_transcript": package.has_transcript,
        "keyframe_method": package.keyframe_method,
        "estimated_tokens": package.estimated_tokens,
        "packaging_latency_ms": round(pack_ms, 1),
        "profile": profile,
        "ffmpeg_version": package.ffmpeg_version,
        "package": package,
    }


def query_provider(name: str, package, question: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    if name == "openai":
        from lvp.providers import OpenAIProvider
        text = OpenAIProvider().query(package, question)
    elif name == "claude":
        from lvp.providers import ClaudeProvider
        text = ClaudeProvider().query(package, question)
    elif name == "gemini":
        from lvp.providers import GeminiProvider
        text = GeminiProvider().query(package, question)
    elif name == "deepseek":
        from lvp.providers import DeepSeekProvider
        text = DeepSeekProvider().query(package, question)
    else:
        raise ValueError(f"Unknown provider: {name}")
    return {
        "provider": name,
        "question": question,
        "answer": text,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        "mode": "lvp_keyframes",
    }


def native_video_stub(provider: str, video: Path, question: str) -> Dict[str, Any]:
    """
    Placeholder for native video API comparisons.

    Implement provider-specific file upload here (Gemini Files API, Claude video,
    etc.). Returns a structured skip until credentials + SDK paths are wired.
    """
    return {
        "provider": provider,
        "question": question,
        "answer": None,
        "latency_ms": None,
        "mode": "native_video",
        "status": "not_implemented",
        "hint": "Wire Gemini Files / Claude video upload in benchmarks/native_video.py",
        "video_bytes": video.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(description="LVP bandwidth/quality comparison harness")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--profile", default="balanced")
    parser.add_argument("--no-transcript", action="store_true")
    parser.add_argument("--query", default=None)
    parser.add_argument("--token-budget", type=int, default=None)
    parser.add_argument("--providers", nargs="*", default=[], help="openai claude gemini")
    parser.add_argument("--questions", nargs="*", default=DEFAULT_QUESTIONS)
    parser.add_argument("--include-native-stub", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Packaging metrics only")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if not args.video.exists():
        raise SystemExit(f"Video not found: {args.video}")

    metrics = package_metrics(
        args.video,
        profile=args.profile,
        transcribe=not args.no_transcript,
        query=args.query,
        token_budget=args.token_budget,
    )
    package = metrics.pop("package")

    answers: List[Dict[str, Any]] = []
    if not args.dry_run:
        for prov in args.providers:
            for q in args.questions:
                try:
                    answers.append(query_provider(prov, package, q))
                except Exception as exc:  # noqa: BLE001 — collect errors in report
                    answers.append({
                        "provider": prov,
                        "question": q,
                        "error": str(exc),
                        "mode": "lvp_keyframes",
                    })
        if args.include_native_stub:
            for prov in args.providers or ["gemini"]:
                answers.append(native_video_stub(prov, args.video, args.questions[0]))

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "answers": answers,
        "notes": [
            "Compression ratios are content-dependent.",
            "Do not treat answer presence as accuracy.",
            "Compare native video APIs separately for fair quality baselines.",
        ],
    }

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        # Avoid dumping huge answers twice when package repr sneaks in
        print(text)

    print(
        f"\nSummary: {metrics['compression_ratio']}x compression, "
        f"{metrics['keyframes']} keyframes, "
        f"{metrics['packaging_latency_ms']} ms packaging",
        flush=True,
    )


if __name__ == "__main__":
    main()
