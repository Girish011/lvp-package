#!/usr/bin/env python3
"""
Download small, license-clear public sample videos for LVP benchmarks.

Sources use direct HTTP URLs (no YouTube scraping). Files land under
benchmarks/data/open_samples/ (gitignored via benchmarks/data/).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "open_samples"

# Curated short / medium public clips (Creative Commons / public domain / sample hosts)
CATALOG = [
    {
        "id": "test_videos_bunny",
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        "license": "Blender Foundation BBB / test-videos.co.uk mirror",
        "category": "animation",
        "notes": "10s Big Buck Bunny ~1MB",
    },
    {
        "id": "filesample_sample_960x400",
        "url": "https://filesamples.com/samples/video/mp4/sample_960x400_ocean_with_audio.mp4",
        "license": "filesamples.com demo clip",
        "category": "nature",
        "notes": "Ocean sample with audio",
    },
    {
        "id": "learningcontainer_small",
        "url": "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
        "license": "learningcontainer sample",
        "category": "speech",
        "notes": "Generic small MP4 sample",
    },
    {
        "id": "w3c_test_fragment",
        "url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        "license": "MDN / CC0 flower clip",
        "category": "nature",
        "notes": "Short flower video from MDN examples",
    },
    {
        "id": "intel_person_detection",
        "url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4",
        "license": "Intel sample-videos (see upstream LICENSE)",
        "category": "action",
        "notes": "Detection demo footage",
    },
    {
        "id": "intel_face_demographics",
        "url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/face-demographics-walking-and-pause.mp4",
        "license": "Intel sample-videos (see upstream LICENSE)",
        "category": "action",
        "notes": "Walking / demographics sample",
    },
    {
        "id": "samplelib_5s",
        "url": "https://download.samplelib.com/mp4/sample-5s.mp4",
        "license": "samplelib.com demo",
        "category": "nature",
        "notes": "5s sample",
    },
    {
        "id": "samplelib_10s",
        "url": "https://download.samplelib.com/mp4/sample-10s.mp4",
        "license": "samplelib.com demo",
        "category": "nature",
        "notes": "10s sample",
    },
    {
        "id": "samplelib_20s",
        "url": "https://download.samplelib.com/mp4/sample-20s.mp4",
        "license": "samplelib.com demo",
        "category": "nature",
        "notes": "20s sample",
    },
]


def _download(url: str, dest: Path, timeout: int = 120) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 10_000:
        print(f"  skip (exists): {dest.name}")
        return True
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "lvp-package-benchmarks/0.2 (+https://github.com/Girish011/lvp-package)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as exc:  # noqa: BLE001
        print(f"  FAIL {url}: {exc}")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return False
    print(f"  ok: {dest.name} ({dest.stat().st_size} bytes)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, default=0, help="Max downloads (0=all)")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manifest = []
    items = CATALOG if not args.limit else CATALOG[: args.limit]
    for item in items:
        dest = args.out / f"{item['id']}.mp4"
        print(f"Fetching {item['id']} ...")
        ok = _download(item["url"], dest)
        entry = dict(item)
        entry["local_path"] = str(dest) if ok else None
        entry["ok"] = ok
        if ok:
            h = hashlib.sha256(dest.read_bytes()).hexdigest()[:16]
            entry["sha256_16"] = h
            entry["bytes"] = dest.stat().st_size
        manifest.append(entry)

    man_path = args.out / "manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ok_n = sum(1 for m in manifest if m["ok"])
    print(f"\nDownloaded {ok_n}/{len(manifest)} → {args.out}")
    print(f"Manifest: {man_path}")


if __name__ == "__main__":
    main()
