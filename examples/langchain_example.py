"""
LangChain + LVP example
=======================

    pip install -e ".[langchain,openai]"
    python examples/langchain_example.py /path/to/video.mp4
"""

from __future__ import annotations

import sys


def main(video_path: str) -> None:
    from lvp.integrations import process_video_to_lvp, as_langchain_tool

    # Plain function
    print(process_video_to_lvp(video_path, profile="minimal", transcribe=False))

    # StructuredTool (requires langchain-core)
    try:
        tool = as_langchain_tool()
        print("Tool name:", tool.name)
        print(tool.invoke({"video_path": video_path, "profile": "minimal", "transcribe": False}))
    except ImportError as exc:
        print("Skipping StructuredTool:", exc)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examples/langchain_example.py <video.mp4>")
        sys.exit(1)
    main(sys.argv[1])
