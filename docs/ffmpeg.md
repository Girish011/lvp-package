# FFmpeg requirements

LVP shells out to the `ffmpeg` / `ffprobe` CLIs. It does **not** link against libav\* ABIs.

## Supported versions

| Version | Status |
|---------|--------|
| **8.x** | Supported (common Homebrew / distro builds) |
| **9.0+** (“Lei”, Aug 2026) | Supported |
| &lt; 8 | Unsupported (may work for basic extract) |

Check your install:

```bash
lvp ffmpeg-info
# or
ffmpeg -version
```

## FFmpeg 9.0 notes

- **`-vsync` was removed.** Use `-fps_mode` (e.g. `-fps_mode vfr`). Older docs/paper text that mentioned `-vsync` are obsolete; the LVP runtime does not pass `-vsync`.
- ABI breaks in libav\* do not affect LVP’s CLI usage.
- Optional future accelerations:
  - **Whisper filter** (8.0+ family builds) — alternative to `openai-whisper`+torch
  - **ONNX / DNN filters** (9.0) — candidate for saliency-based keyframes

## What LVP calls today

1. Scene detection: `select=gt(scene,T)` + `showinfo`
2. Frame grab: `-ss` + `-vframes 1` + `scale` + WebP `-quality`
3. Audio extract for Whisper: PCM 16 kHz mono

## CI

GitHub Actions installs distro FFmpeg on `ubuntu-latest` (typically 8.x-line or distro default) and runs `lvp ffmpeg-info` plus pytest.
