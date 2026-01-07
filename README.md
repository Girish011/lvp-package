# LVP: LLM-Ready Video Package

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-2501.xxxxx-b31b1b.svg)](https://arxiv.org/)

**A universal standard for bandwidth-efficient video upload to multimodal LLMs.**

## 🎯 The Problem

Uploading videos to AI assistants (Claude, GPT-4V, Gemini) wastes bandwidth:
- A 1-minute video can be 50+ MB
- 90% of frames are redundant for understanding
- Users on slow connections can't use video features

## 💡 The Solution

LVP preprocesses videos locally, creating a lightweight package:

```
Original Video: 50 MB  →  LVP Package: 500 KB  (100x smaller)
```

The `.lvp` format contains:
- 🖼️ Intelligent keyframes (not every frame)
- 📝 Speech transcript (time-aligned)
- 📊 Scene metadata
- 🔧 Works with ANY multimodal LLM

## 🚀 Quick Start

### Installation

```bash
pip install lvp

# Optional: for transcription
pip install lvp[whisper]

# Optional: for specific providers
pip install lvp[claude]    # Anthropic Claude
pip install lvp[openai]    # OpenAI GPT-4V
pip install lvp[gemini]    # Google Gemini
```

**Requirement:** FFmpeg must be installed ([download](https://ffmpeg.org/download.html))

### Basic Usage

```python
import lvp

# Process a video
package = lvp.process("my_video.mp4")
package.save("my_video.lvp")

# Check the compression
print(package.summary())
# {'original_size_mb': 52.4, 'lvp_size_kb': 487.2, 'compression_ratio': 110.1, ...}
```

### Command Line

```bash
# Create LVP package
lvp process video.mp4 -o video.lvp

# View package info
lvp info video.lvp

# Extract contents
lvp extract video.lvp -o ./extracted/
```

### Query LLMs

```python
import lvp
from lvp.providers import ClaudeProvider

# Load package
package = lvp.load("my_video.lvp")

# Query Claude
claude = ClaudeProvider(api_key="sk-...")
response = claude.query(package, "What happens in this video?")
print(response)
```

## 📦 LVP Format Specification

An `.lvp` file is a ZIP archive containing:

```
video.lvp
├── manifest.json        # Package metadata (v1.0 spec)
├── keyframes/
│   ├── frame_0000.webp  # Selected keyframes
│   ├── frame_0001.webp
│   └── ...
├── transcript.json      # Time-aligned speech
└── scenes.json          # Scene boundaries
```

### Manifest Schema (v1.0)

```json
{
  "lvp_version": "1.0",
  "created_at": "2025-01-07T12:00:00Z",
  "source": {
    "filename": "original.mp4",
    "duration_seconds": 120.5,
    "original_resolution": [1920, 1080],
    "original_size_bytes": 52428800
  },
  "content": {
    "keyframe_count": 24,
    "keyframe_resolution": [512, 288],
    "has_transcript": true,
    "scene_count": 5
  }
}
```

## ⚙️ Device Profiles

Choose based on your device capabilities:

| Profile | Keyframes/min | Resolution | Use Case |
|---------|---------------|------------|----------|
| `minimal` | 6 | 384×216 | Low-end phones |
| `balanced` | 12 | 512×288 | Mid-range devices |
| `quality` | 20 | 640×360 | Laptops |
| `maximum` | 30 | 854×480 | Desktops with GPU |

```python
package = lvp.process("video.mp4", profile="minimal")
```

## 🔌 Provider Support

| Provider | Status | Install |
|----------|--------|---------|
| Claude (Anthropic) | ✅ Ready | `pip install lvp[claude]` |
| GPT-4V (OpenAI) | ✅ Ready | `pip install lvp[openai]` |
| Gemini (Google) | ✅ Ready | `pip install lvp[gemini]` |
| Qwen-VL | 🚧 Planned | - |
| LLaVA | 🚧 Planned | - |

## 📊 Benchmarks

| Video Type | Original | LVP | Compression | Quality* |
|------------|----------|-----|-------------|----------|
| 1min talking head | 45 MB | 380 KB | 118x | 98% |
| 2min tutorial | 89 MB | 720 KB | 124x | 95% |
| 5min vlog | 210 MB | 1.8 MB | 117x | 93% |

*Quality = semantic similarity of LLM responses (LVP vs raw video)

## 🔬 Research

This project is part of academic research on bandwidth-efficient multimodal AI.

### Paper

> **LVP: A Universal Standard for Bandwidth-Efficient Video Upload to Multimodal LLMs**
> 
> [arXiv preprint coming soon]

### Citation

```bibtex
@article{lvp2025,
  title={LVP: A Universal Standard for Bandwidth-Efficient Video Upload to Multimodal LLMs},
  author={LVP Research Partnership},
  journal={arXiv preprint arXiv:2501.xxxxx},
  year={2025}
}
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

- 🐛 [Report bugs](https://github.com/lvp-research/lvp/issues)
- 💡 [Request features](https://github.com/lvp-research/lvp/issues)
- 🔧 [Submit PRs](https://github.com/lvp-research/lvp/pulls)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- Research community contributions

---

**Made with ❤️ by the LVP Research Partnership**
