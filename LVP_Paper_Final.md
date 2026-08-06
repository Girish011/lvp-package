# LVP: Edge Semantic Packaging for Bandwidth-Efficient Video Input to Multimodal LLMs

**Authors:** Girish Sekar  
**Affiliations:** Independent Researcher  
**Acknowledgments:** Claude (Anthropic) was used to assist with portions of code and manuscript drafting; experiments and verification were conducted by the author.  
**Repository:** https://github.com/Girish011/lvp-package  
**Date:** August 2026 (revised draft)

---

## Abstract

Multimodal LLMs increasingly accept video, but uploading raw files remains costly in bandwidth, tokens, and dollars — and some APIs still prefer image+text inputs. We present **LVP (LLM-Ready Video Package)**, an open edge preprocessor and ZIP-based interchange format that extracts scene-aware WebP keyframes, optional Whisper transcripts, and scene metadata for multimodal APIs. LVP targets **bandwidth, cost, privacy, and provider portability**, complementing (not replacing) native video ingest in Gemini, Claude, and similar systems.

On an early five-video pilot (short UGC clips), LVP reduced payload size by roughly **13–189×** (mean ~**61×**). Quality claims from that pilot were qualitative and are **not** presented as benchmark accuracy. This draft reframes the contribution as a systems tool and describes a public evaluation plan (native-video baselines, cost/bandwidth metrics, Video-MME-style subsets). We release a Python SDK with query-aware / token-budget selection and long-video chunking.

**Keywords:** Video preprocessing, Multimodal LLMs, Bandwidth optimization, Edge computing, Keyframe selection

---

## 1. Introduction

Vision-language models can analyze video content, but transmitting full files (often tens to hundreds of MB) creates barriers for metered networks, mobile clients, and cost-sensitive apps. Many semantic queries do not need every frame; speech is often better represented as text; and applications may need a **deterministic offline package** with a predictable token budget.

**LVP** addresses this with three practical contributions:

1. **Format**: A portable ZIP (`.lvp`) of keyframes + transcript + scene metadata  
2. **Pipeline**: Device profiles, scene-adaptive sampling, query-aware / token-budget selection, and long-video chunking  
3. **SDK**: Provider adapters for Claude, OpenAI, and Gemini image APIs  

We do **not** claim LVP as a universal standard or as strictly superior to native video APIs on understanding quality.

---

## 2. Related Work

Keyframe selection for VLMs (e.g. AKS, KeyVideoLLM, KVTP) typically optimizes **in-model** token use. Edge–cloud video analytics systems target streaming/surveillance. Classical codecs optimize perceptual fidelity. LVP sits in between: **client-side semantic packaging for LLM I/O**, emphasizing upload size and multi-provider interchange rather than SOTA VideoQA accuracy.

Native video APIs (Gemini Files, Claude video, product ChatGPT) have reduced the need for custom packaging for some users; LVP remains relevant for bandwidth, privacy, cost caps, and image-only backends.

---

## 3. LVP Format Specification

### 3.1 Design Principles

1. **Provider-agnostic** image+text consumption  
2. **Self-contained** single file  
3. **Extensible** JSON metadata  
4. **Efficient** WebP keyframes  

### 3.2 Package Structure

```
video.lvp
├── manifest.json
├── keyframes/*.webp
├── transcript.json
└── scenes.json
```

### 3.3 Design Rationale

WebP compresses stills well for API upload. ZIP is ubiquitous. Separating transcript enables text-only or hybrid queries without re-uploading images.

---

## 4. Preprocessing Pipeline

1. **Analysis**: ffprobe metadata + FFmpeg scene detection (`select=gt(scene,T)`)  
2. **Selection**: scene-adaptive sampling; optional **query-aware** ranking under a token budget  
3. **Processing**: resize + WebP; optional Whisper ASR  
4. **Packaging**: ZIP + manifest  

**FFmpeg note:** Documentation previously mentioned `-vsync vfr`. **`-vsync` was removed in FFmpeg 9.0**; use `-fps_mode` instead. The LVP runtime does not rely on `-vsync`. Supported targets: **FFmpeg 8.x and 9.0+**.

### 4.1 Device Profiles

| Profile | Keyframes/min | Resolution | WebP Quality |
|---------|---------------|------------|--------------|
| minimal | 6 | 384×216 | 60 |
| balanced | 12 | 512×288 | 75 |
| quality | 20 | 640×360 | 85 |
| maximum | 30 | 854×480 | 90 |

### 4.2 Long-video chunking

Videos longer than a configured window (default 10 minutes) can be split into overlapping segments, each packaged as `.lvp`, with a JSON chunk manifest for multi-turn analysis.

---

## 5. Evaluation (status)

### 5.1 Pilot (January 2026) — illustrative only

Five short clips (screen, animation, indoor, TEDx, outdoor). LVP→GPT-4o image API; informal comparison to ChatGPT UI raw upload. **Compression** roughly 13–189× (mean ~61×). “Questions answered” counts are **not** ground-truth accuracy. Cross-provider testing was incomplete; some automated comparison runs failed (environment/API issues).

### 5.2 Required evaluation for arXiv v1

1. Public subsets (Video-MME / MVBench / EgoSchema-style)  
2. Fair baselines: native video APIs + uniform frames + LVP ± transcript  
3. Metrics: task score, upload MB, tokens, $, latency; ablations  
4. Stress tests: OCR, action, long video, multilingual/noisy ASR  
5. Honest failure analysis  

Harness: `benchmarks/` in the repository.

---

## 6. Implementation

```python
import lvp
package = lvp.process("video.mp4", profile="balanced", query="...", token_budget=8000)
package.save("video.lvp")
```

Requirements: Python 3.9+, FFmpeg 8+, optional Whisper and provider SDKs. No GPU required for core packaging.

---

## 7. Discussion & Limitations

**Strengths:** bandwidth reduction, privacy, predictable budgets, multi-provider portability, transcript helps speech-heavy content.

**Limitations:** fast motion and fine OCR can suffer; Whisper quality varies; local preprocess adds latency; algorithmic novelty is modest (systems contribution).

LVP should be positioned as **ffmpeg-for-LLM-video-inputs**, not as a VideoQA SOTA method.

---

## 8. Broader Impact

Positive: accessibility on metered networks; reduced transmission energy; on-device privacy. Risks: easier large-scale video triage. Encourage responsible use.

---

## 9. Future Work

- Optional FFmpeg Whisper filter / ONNX DNN saliency (FFmpeg 8–9)  
- Stronger embedding-based query-aware selection  
- Continuous public benchmark dashboards  
- Framework integrations (LangChain, etc.)  

---

## 10. Conclusion

LVP is an open edge packaging layer for multimodal LLM video I/O. Compression benefits are clear; quality parity with native video is **task-dependent** and must be measured with modern APIs. We release the SDK at https://github.com/Girish011/lvp-package.

---

## References

1. Anthropic. Claude documentation (video / vision), 2025–2026.  
2. OpenAI. GPT-4o System Card / API docs.  
3. Google DeepMind. Gemini multimodal / Files API.  
4. Maaz et al. Video-ChatGPT. arXiv:2306.05424, 2023.  
5. Zhang et al. Video-LLaMA. arXiv:2306.02858, 2023.  
6. Tang et al. Adaptive Keyframe Sampling. CVPR 2025.  
7. KeyVideoLLM. arXiv:2407.03104, 2024.  
8. Radford et al. Whisper. 2022.  
9. FFmpeg 9.0 release notes (Lei), August 2026 — `-vsync` removed in favor of `-fps_mode`.  

---

## Appendix: Reproduction

```bash
git clone https://github.com/Girish011/lvp-package.git
cd lvp-package
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -q
lvp process path/to/video.mp4 -o video.lvp
```

*Draft revised August 2026 for honest scope prior to arXiv submission.*
