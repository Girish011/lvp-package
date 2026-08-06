# LVP: LLM-Ready Video Package

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Girish011/lvp-package/actions/workflows/ci.yml/badge.svg)](https://github.com/Girish011/lvp-package/actions/workflows/ci.yml)

**Edge preprocessing for bandwidth-, token-, and cost-efficient video input to multimodal LLMs.**

LVP runs on your machine (FFmpeg + optional Whisper), extracts scene-aware WebP keyframes and a speech transcript, and packs them into a small `.lvp` ZIP. You send that package to Claude, GPT-4o, Gemini, or any vision API — instead of uploading the raw video.

LVP is a **complement** to native video APIs (Gemini, Claude video, etc.), not a replacement. Use it when you care about upload size, predictable token budgets, privacy (raw video stays local), or multi-provider image+text backends.

---

## Why LVP

| Goal | What LVP does |
|------|----------------|
| Bandwidth | Typical compression on short clips: **~13–60×+** (content-dependent) |
| Cost / tokens | Cap keyframes via profiles or `--token-budget` |
| Privacy | Raw MP4 never needs to leave the device |
| Portability | Same `.lvp` works across Claude / OpenAI / Gemini image APIs |

Native video upload often wins on fast motion, fine OCR, and long temporal reasoning. Measure both paths with [`benchmarks/`](benchmarks/).

---

## Quick Start

### Requirements

- Python 3.9+
- **FFmpeg 8.0+** (9.0 supported; see [docs/ffmpeg.md](docs/ffmpeg.md))
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg` (or distro equivalent)

### Installation

```bash
git clone https://github.com/Girish011/lvp-package.git
cd lvp-package
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Optional: transcription + providers
pip install -e ".[whisper,openai,claude,gemini]"
```

PyPI (when published):

```bash
pip install lvp-package
# or: pip install lvp
```

---

## Usage

### CLI

```bash
# Process a video
lvp process video.mp4 -o video.lvp

# Query-aware + token budget
lvp process video.mp4 --query "What does the speaker conclude?" --token-budget 8000

# Long videos → overlapping chunks
lvp chunk long.mp4 -o ./chunks/ --chunk-duration 600

# Inspect
lvp info video.lvp
lvp ffmpeg-info
```

### Python API

```python
import lvp

package = lvp.process("video.mp4", profile="balanced")
package.save("video.lvp")
print(package.summary())

# Query-aware selection
package = lvp.process(
    "talk.mp4",
    query="What is the punchline?",
    token_budget=8000,
)

# Long video
result = lvp.process_chunked("hour.mp4", chunk_duration=600, output_dir="./chunks")
```

### Query an LLM

```python
from lvp.providers import OpenAIProvider, ClaudeProvider, GeminiProvider

package = lvp.load("video.lvp")
answer = OpenAIProvider().query(package, "What happens in this video?")
print(answer)
```

LangChain tool: see [`examples/langchain_example.py`](examples/langchain_example.py).

---

## Package format

```
video.lvp          # ZIP archive
├── manifest.json
├── keyframes/*.webp
├── transcript.json
└── scenes.json
```

Full schema: [docs/format.md](docs/format.md).

---

## Device profiles

| Profile | Keyframes/min | Resolution | Use case |
|---------|---------------|------------|----------|
| `minimal` | 6 | 384×216 | Low bandwidth / mobile |
| `balanced` | 12 | 512×288 | Default |
| `quality` | 20 | 640×360 | Higher detail |
| `maximum` | 30 | 854×480 | Max local detail |

---

## FFmpeg compatibility

| Version | Status |
|---------|--------|
| 8.x | Supported (current Homebrew stable) |
| 9.0+ | Supported — do **not** use `-vsync` (removed); LVP uses `-fps_mode` when needed |
| &lt; 8 | Unsupported (may still work for basic extract) |

```bash
lvp ffmpeg-info
```

---

## Evaluation & benchmarks

See [`benchmarks/README.md`](benchmarks/README.md) for:

- LVP vs native video upload (when API supports it)
- Bandwidth / estimated tokens / latency tables
- Stress categories: OCR, action, long video, multilingual ASR
- Download helpers for public video-QA subsets

Early lab results (5 short clips, GPT-4o, Jan 2026) showed **~13–189×** size reduction (avg ~61×). Those numbers are **illustrative**, not a claim of universal quality parity. Re-run the harness before citing figures.

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

---

## Roadmap

- [x] Core pipeline + CLI
- [x] Claude / OpenAI / Gemini providers
- [x] Query-aware + token-budget selection
- [x] Long-video chunking
- [x] FFmpeg 8.x / 9.0 compatibility helpers
- [ ] Optional FFmpeg Whisper / ONNX DNN acceleration
- [ ] Broader public-benchmark results published continuously

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

---

## Citation

```bibtex
@misc{sekar2026lvp,
  title={LVP: Edge Semantic Packaging for Bandwidth-Efficient Video Input to Multimodal LLMs},
  author={Sekar, Girish},
  year={2026},
  howpublished={GitHub},
  url={https://github.com/Girish011/lvp-package}
}
```

Draft paper: [`LVP_Paper_Final.md`](LVP_Paper_Final.md) (claims being revised for arXiv; treat as draft).

---

## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <b>Save bandwidth. Cap tokens. Keep raw video local.</b>
</p>
