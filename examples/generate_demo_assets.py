#!/usr/bin/env python3
"""
Generate a simple before/after demo assets folder.

Creates a synthetic MP4, builds an LVP, and writes demo_stats.json.
Optionally prints an HTML snippet you can screenshot for the README.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples" / "demo_assets"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    video = OUT / "demo.mp4"
    lvp_path = OUT / "demo.lvp"

    if not video.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "smptebars=size=640x360:rate=25",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=5",
                "-t",
                "5",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-y",
                str(video),
            ],
            check=True,
            capture_output=True,
        )

    import lvp

    pkg = lvp.process(str(video), output=str(lvp_path), profile="balanced", transcribe=False)
    stats = {
        "original_bytes": video.stat().st_size,
        "lvp_bytes": lvp_path.stat().st_size,
        "compression_ratio": round(video.stat().st_size / lvp_path.stat().st_size, 2),
        "keyframes": pkg.keyframe_count,
        "summary": pkg.summary(),
    }
    (OUT / "demo_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    html = OUT / "demo_card.html"
    html.write_text(
        f"""<!doctype html>
<html><head><meta charset='utf-8'><title>LVP demo</title>
<style>
body{{font-family:ui-sans-serif,system-ui;background:#0b1020;color:#e8eefc;display:flex;min-height:100vh;align-items:center;justify-content:center}}
card{{background:#141b2d;padding:2rem 2.5rem;border-radius:16px;max-width:520px}}
h1{{margin:0 0 .5rem;font-size:1.4rem}}
.row{{display:flex;justify-content:space-between;margin:.4rem 0;opacity:.95}}
.big{{font-size:2rem;font-weight:700;margin:1rem 0}}
</style></head><body><card>
<h1>LVP — local video → tiny package</h1>
<div class='row'><span>Original MP4</span><strong>{stats['original_bytes']/1024:.1f} KB</strong></div>
<div class='row'><span>LVP package</span><strong>{stats['lvp_bytes']/1024:.1f} KB</strong></div>
<div class='big'>{stats['compression_ratio']}× smaller</div>
<div class='row'><span>Keyframes</span><strong>{stats['keyframes']}</strong></div>
<p style='opacity:.7;font-size:.9rem;margin-top:1.2rem'>Screenshot this card for the README demo.</p>
</card></body></html>
""",
        encoding="utf-8",
    )
    print(json.dumps(stats, indent=2))
    print(f"Wrote {html}")


if __name__ == "__main__":
    main()
