"""LangChain-compatible tools for LVP packaging."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LVPProcessInput(BaseModel):
    video_path: str = Field(..., description="Path to a local video file")
    profile: str = Field(
        "balanced",
        description="Device profile: minimal | balanced | quality | maximum",
    )
    output_path: Optional[str] = Field(
        None, description="Optional .lvp output path"
    )
    query: Optional[str] = Field(
        None, description="Optional question for query-aware keyframe selection"
    )
    token_budget: Optional[int] = Field(
        None, description="Optional approximate vision token budget"
    )
    transcribe: bool = Field(True, description="Include Whisper transcript when available")


def process_video_to_lvp(
    video_path: str,
    profile: str = "balanced",
    output_path: Optional[str] = None,
    query: Optional[str] = None,
    token_budget: Optional[int] = None,
    transcribe: bool = True,
) -> str:
    """
    Process a video into an LVP package and return a summary string.

    Usable as a plain function or wrapped as a LangChain StructuredTool.
    """
    import lvp

    out = output_path
    if out is None:
        out = video_path.rsplit(".", 1)[0] + ".lvp"

    package = lvp.process(
        video_path,
        output=out,
        profile=profile,
        transcribe=transcribe,
        query=query,
        token_budget=token_budget,
    )
    summary = package.summary()
    return (
        f"Saved {out}. Compression={summary.get('compression_ratio')}x, "
        f"keyframes={summary.get('keyframes')}, "
        f"estimated_tokens={summary.get('estimated_tokens')}"
    )


def as_langchain_tool():
    """
    Return a LangChain StructuredTool if langchain_core is installed.

        from lvp.integrations.langchain_tool import as_langchain_tool
        tool = as_langchain_tool()
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as exc:
        raise ImportError(
            "langchain-core required. Install with: pip install -e \".[langchain]\""
        ) from exc

    return StructuredTool.from_function(
        func=process_video_to_lvp,
        name="lvp_process_video",
        description=(
            "Preprocess a local video into a compact LVP package (keyframes + "
            "transcript) for bandwidth-efficient multimodal LLM input."
        ),
        args_schema=LVPProcessInput,
    )


__all__ = [
    "LVPProcessInput",
    "as_langchain_tool",
    "process_video_to_lvp",
]
