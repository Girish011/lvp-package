# Community launch guide

Checklist to make LVP discoverable without overclaiming.

## Before announcing

- [x] Honest README (bandwidth/privacy/cost; not “beats native video”)
- [x] CI + tests
- [x] Docs (`docs/`), CHANGELOG, SECURITY, CONTRIBUTING
- [ ] PyPI release (see below)
- [ ] GitHub repo description + topics: `video`, `llm`, `ffmpeg`, `whisper`, `multimodal`
- [ ] One demo GIF or Colab link in README

## PyPI publish

Package name on PyPI: **`lvp-package`** (import name remains `lvp`).

```bash
pip install -e ".[dev]"
python -m build
# twine upload dist/*   # requires PyPI API token
```

Verify locally:

```bash
pip install dist/lvp_package-*.whl
lvp --version
```

## Show HN / Reddit draft

**Title:** Show HN: LVP – preprocess video locally before sending it to Claude/GPT/Gemini

**Body (short):**

> Uploading raw video to multimodal APIs burns bandwidth and tokens. LVP is a small Python tool (FFmpeg + optional Whisper) that builds a `.lvp` ZIP of WebP keyframes + transcript so you can query vision APIs with a much smaller payload. Raw video can stay on-device.
>
> It is a complement to native video APIs, not a claim of better understanding. Repo: https://github.com/Girish011/lvp-package

Post to: Show HN, r/LocalLLaMA, r/MachineLearning (self-post Friday), relevant Discord servers.

## arXiv

1. Finish `benchmarks/` tables vs native video  
2. Keep thesis: edge semantic packaging / cost-bandwidth tradeoffs  
3. Submit revised [`LVP_Paper_Final.md`](LVP_Paper_Final.md) via arXiv (cs.MM / cs.AI)  
4. Replace any arXiv badge only after the ID exists  

## Integrations that attract stars

- LangChain tool (`examples/langchain_example.py`) — done  
- FastAPI microservice sketch — good first issue  
- Cursor/Claude skill wrapping `lvp process` — good first issue  
