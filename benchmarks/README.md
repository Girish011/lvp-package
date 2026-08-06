# Benchmarks

LVP is an **edge packaging** tool. Evaluate it on **bandwidth, tokens, cost, latency, and task quality** against native video upload — not only “did the model answer.”

## Quick start

```bash
pip install -e ".[dev,openai,gemini,claude]"

# Synthetic local smoke (no API keys)
python benchmarks/run_comparison.py --video tests/fixtures/sample_colorbars.mp4 --dry-run

# With OpenAI keyframes path
export OPENAI_API_KEY=...
python benchmarks/run_comparison.py --video path/to/clip.mp4 --providers openai --out results.json
```

## Metrics

| Metric | Meaning |
|--------|---------|
| `original_bytes` / `lvp_bytes` | Upload size proxy |
| `compression_ratio` | original / lvp |
| `estimated_tokens` | Rough vision+text token estimate |
| `latency_ms` | Wall time for packaging and/or API |
| `answer` | Model text (manual or LLM-as-judge later) |

## Stress categories

See `stress_categories.json` and download helpers:

| Category | Intent |
|----------|--------|
| `ocr` | Dense on-screen text |
| `action` | Fast motion / sports |
| `speech` | Talks / meetings |
| `long` | >10 minutes (use chunking) |
| `multilingual_asr` | Non-English / noisy audio |
| `privacy` | Prefer local Whisper only |

## Public datasets

`download_benchmarks.py` prints instructions and optional wget/curl commands for **subsets** of public VideoQA resources (Video-MME, MVBench, EgoSchema). It does **not** vendor multi-GB corpora into git.

## Fair baselines

1. **LVP** (keyframes ± transcript) → vision API  
2. **Uniform frames** (same N, no scene detect)  
3. **Native video** (Gemini Files / Claude video) when available  
4. Ablate: profile, transcript on/off, query-aware on/off  

Publish tables as JSON under `benchmarks/results/` (gitignored by default except `results/.gitkeep`).
