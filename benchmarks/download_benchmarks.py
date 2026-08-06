#!/usr/bin/env python3
"""
Print download / setup instructions for public video understanding subsets.

We intentionally do not auto-download multi-GB datasets. This script helps
reproduce an evaluation layout under benchmarks/data/.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

DATASETS = {
    "video-mme": {
        "description": "Video-MME — multi-choice video understanding benchmark",
        "homepage": "https://video-mme.github.io/",
        "notes": [
            "Download the official release and place a small subset under benchmarks/data/video-mme/",
            "Prefer short clips first for bandwidth tables.",
        ],
    },
    "mvbench": {
        "description": "MVBench — multi-task video reasoning",
        "homepage": "https://huggingface.co/datasets/OpenGVLab/MVBench",
        "notes": [
            "Use Hugging Face datasets or the authors' release.",
            "Map tasks to stress categories in stress_categories.json.",
        ],
    },
    "egoschema": {
        "description": "EgoSchema — long-form egocentric video QA",
        "homepage": "https://egoschema.github.io/",
        "notes": [
            "Ideal for chunking + long-video stress tests.",
            "Keep only a licensed subset for CI-sized demos.",
        ],
    },
    "activitynet-qa": {
        "description": "ActivityNet-QA",
        "homepage": "https://github.com/MILVLG/activitynet-qa",
        "notes": [
            "Pair with ActivityNet videos under your data license constraints.",
        ],
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List known datasets")
    parser.add_argument("--init", action="store_true", help="Create data/ directory layout")
    parser.add_argument("--dataset", choices=sorted(DATASETS.keys()), help="Show one dataset")
    args = parser.parse_args()

    if args.init:
        for name, meta in DATASETS.items():
            (DATA / name).mkdir(parents=True, exist_ok=True)
            readme = DATA / name / "README.md"
            if not readme.exists():
                readme.write_text(
                    f"# {name}\n\n{meta['description']}\n\n"
                    f"Homepage: {meta['homepage']}\n\n"
                    + "\n".join(f"- {n}" for n in meta["notes"])
                    + "\n",
                    encoding="utf-8",
                )
        print(f"Initialized {DATA}")
        return

    if args.dataset:
        print(json.dumps(DATASETS[args.dataset], indent=2))
        return

    # default: list
    for name, meta in DATASETS.items():
        print(f"{name}: {meta['description']}")
        print(f"  {meta['homepage']}")
    print("\nRun with --init to create benchmarks/data/<name>/ folders.")


if __name__ == "__main__":
    main()
