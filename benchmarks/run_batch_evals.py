#!/usr/bin/env python3
"""
Batch-run LVP packaging + provider Q&A over a video list.

Usage:
  export DEEPSEEK_API_KEY=...
  python benchmarks/run_batch_evals.py --providers deepseek
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.run_comparison import DEFAULT_QUESTIONS, package_metrics, query_provider  # noqa: E402
from benchmarks.metrics import bandwidth_row  # noqa: E402


def collect_videos(paths: list[Path]) -> list[Path]:
    vids: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() == ".mp4":
            vids.append(p)
        elif p.is_dir():
            vids.extend(sorted(p.glob("*.mp4")))
    # de-dupe
    seen = set()
    out = []
    for v in vids:
        key = str(v.resolve())
        if key not in seen:
            seen.add(key)
            out.append(v)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--videos",
        nargs="+",
        type=Path,
        default=[
            ROOT / "uploads",
            ROOT / "benchmarks" / "data" / "open_samples",
        ],
    )
    parser.add_argument("--providers", nargs="+", default=["deepseek"])
    parser.add_argument("--profile", default="balanced")
    parser.add_argument("--no-transcript", action="store_true")
    parser.add_argument("--max-questions", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0, help="Max videos (0=all)")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "benchmarks" / "results" / "batch_deepseek.json",
    )
    args = parser.parse_args()

    videos = collect_videos(args.videos)
    if args.limit:
        videos = videos[: args.limit]
    if not videos:
        raise SystemExit("No mp4 videos found")

    questions = DEFAULT_QUESTIONS[: args.max_questions]
    rows = []
    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] {video.name}", flush=True)
        try:
            metrics = package_metrics(
                video,
                profile=args.profile,
                transcribe=not args.no_transcript,
                query=None,
                token_budget=None,
            )
            package = metrics.pop("package")
            bw = bandwidth_row(
                metrics["original_bytes"],
                metrics["lvp_bytes"],
                metrics.get("estimated_tokens") or 0,
                price_key="openai:gpt-4o",
            )
            answers = []
            for prov in args.providers:
                for q in questions:
                    try:
                        answers.append(query_provider(prov, package, q))
                        print(f"  {prov}: ok ({q[:40]}...)", flush=True)
                    except Exception as exc:  # noqa: BLE001
                        answers.append(
                            {
                                "provider": prov,
                                "question": q,
                                "error": str(exc),
                                "mode": "lvp_keyframes",
                            }
                        )
                        print(f"  {prov}: ERROR {exc}", flush=True)
            rows.append(
                {
                    "video": str(video),
                    "metrics": metrics,
                    "bandwidth": bw,
                    "answers": answers,
                }
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  packaging ERROR: {exc}", flush=True)
            rows.append({"video": str(video), "error": str(exc)})

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "providers": args.providers,
        "profile": args.profile,
        "video_count": len(videos),
        "rows": rows,
        "summary": _summarize(rows),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {args.out}")
    print(json.dumps(report["summary"], indent=2))


def _summarize(rows: list) -> dict:
    ok = [r for r in rows if "metrics" in r]
    if not ok:
        return {"videos_ok": 0}
    ratios = [r["metrics"]["compression_ratio"] for r in ok if r["metrics"].get("compression_ratio")]
    ans_ok = sum(
        1
        for r in ok
        for a in r.get("answers", [])
        if a.get("answer") and not a.get("error")
    )
    ans_err = sum(1 for r in ok for a in r.get("answers", []) if a.get("error"))
    return {
        "videos_ok": len(ok),
        "avg_compression_ratio": round(sum(ratios) / len(ratios), 2) if ratios else None,
        "min_compression_ratio": min(ratios) if ratios else None,
        "max_compression_ratio": max(ratios) if ratios else None,
        "answers_ok": ans_ok,
        "answers_error": ans_err,
        "text_only_fallbacks": sum(
            1
            for r in ok
            for a in r.get("answers", [])
            if isinstance(a.get("answer"), str)
            and a["answer"].startswith("[deepseek:image_fallback_text_only]")
        ),
    }


if __name__ == "__main__":
    main()
