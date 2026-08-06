# LVP Format Specification (v1.0)

An `.lvp` file is a ZIP archive with Deflate compression.

## Layout

```
package.lvp
├── manifest.json
├── keyframes/
│   ├── frame_0000.webp
│   └── ...
├── transcript.json
└── scenes.json
```

## manifest.json

| Field | Description |
|-------|-------------|
| `lvp_version` | Format version string (`1.0`) |
| `created_at` | ISO-8601 timestamp |
| `source.*` | Original filename, duration, resolution, bytes |
| `processing.device_profile` | `minimal` / `balanced` / `quality` / `maximum` |
| `processing.keyframe_method` | `scene_adaptive` / `query_aware` / `token_budget` |
| `processing.keyframe_timestamps` | Seconds |
| `processing.query` | Optional query string |
| `processing.estimated_tokens` | Rough token estimate |
| `processing.ffmpeg_version` | FFmpeg used at build time |
| `content.*` | Counts and keyframe resolution |

## transcript.json

Whisper-style object:

```json
{
  "language": "en",
  "full_text": "...",
  "segments": [
    {"start": 0.0, "end": 1.2, "text": "...", "confidence": 1.0, "aligned_keyframes": []}
  ]
}
```

If Whisper is not installed, `full_text` may be a placeholder starting with `[`.

## scenes.json

```json
{
  "scenes": [
    {
      "scene_id": 0,
      "start_time": 0.0,
      "end_time": 5.0,
      "keyframe_indices": [0, 1]
    }
  ]
}
```

## Chunk manifests

`lvp chunk` also writes `<name>_chunks.json` describing overlapping segment packages (see `lvp.core.chunking.ChunkedLVPResult`).
