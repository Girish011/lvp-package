"""Cost / bandwidth helpers for evaluation tables."""

from __future__ import annotations

from typing import Any

# Rough public list prices — update as providers change. USD per 1M tokens.
DEFAULT_PRICE_PER_MTONEN = {
    "openai:gpt-4o": {"input": 2.50, "output": 10.0},
    "claude:sonnet": {"input": 3.0, "output": 15.0},
    "gemini:flash": {"input": 0.10, "output": 0.40},
}


def estimate_cost_usd(
    input_tokens: int,
    output_tokens: int = 500,
    price_key: str = "openai:gpt-4o",
    prices: dict[str, dict[str, float]] | None = None,
) -> float:
    table = prices or DEFAULT_PRICE_PER_MTONEN
    row = table[price_key]
    return (input_tokens * row["input"] + output_tokens * row["output"]) / 1_000_000


def bandwidth_row(
    original_bytes: int,
    lvp_bytes: int,
    estimated_tokens: int,
    price_key: str = "openai:gpt-4o",
) -> dict[str, Any]:
    return {
        "original_mb": round(original_bytes / 1e6, 3),
        "lvp_mb": round(lvp_bytes / 1e6, 3),
        "saved_mb": round((original_bytes - lvp_bytes) / 1e6, 3),
        "compression_ratio": round(original_bytes / lvp_bytes, 2) if lvp_bytes else None,
        "estimated_input_tokens": estimated_tokens,
        "est_cost_usd_lvp": round(estimate_cost_usd(estimated_tokens, price_key=price_key), 6),
    }
