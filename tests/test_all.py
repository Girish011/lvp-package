"""
Manual smoke test (optional). Prefer: pytest tests/

Usage:
  python tests/test_all.py [path/to/video.mp4]
"""

from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    video = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "uploads" / "test_audio_video.mp4"
    if not video.exists():
        print(f"Video not found: {video}")
        print("Pass a path or run: pytest tests/")
        sys.exit(1)

    import lvp

    out = video.with_suffix(".lvp")
    print("Processing", video)
    lvp.process(str(video), output=str(out), profile="minimal", transcribe=False)
    with zipfile.ZipFile(out) as z:
        kf = [n for n in z.namelist() if n.startswith("keyframes/")]
        print("keyframes in zip:", len(kf))
    loaded = lvp.load(str(out))
    print("summary:", loaded.summary())

    if os.getenv("OPENAI_API_KEY"):
        from lvp.providers import OpenAIProvider
        print(OpenAIProvider().query(loaded, "What is shown in this video?"))
    else:
        print("OPENAI_API_KEY not set; skipping provider call")


if __name__ == "__main__":
    main()
