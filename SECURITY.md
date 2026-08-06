# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes |
| 0.1.x   | Best-effort |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

1. Use GitHub [Security Advisories](https://github.com/Girish011/lvp-package/security/advisories/new) if available, or
2. Contact the repository owner via GitHub: https://github.com/Girish011

Include steps to reproduce, impact, and any suggested fix.

## Scope notes

- LVP shells out to local `ffmpeg` / `ffprobe`. Keep FFmpeg updated.
- Never commit API keys. Provider clients read `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`.
- Processing untrusted video files inherits FFmpeg/Whisper attack surface; sandbox untrusted inputs in production.
