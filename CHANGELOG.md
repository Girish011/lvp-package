# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-06

### Added
- Query-aware and token-budget keyframe selection (`--query`, `--token-budget`)
- Long-video chunking (`lvp chunk` / `lvp.process_chunked`)
- FFmpeg 8.x / 9.0 compatibility helpers (`lvp ffmpeg-info`)
- Real pytest suite with generated fixture video
- Benchmarks harness and dataset download scripts
- Docs: format spec, FFmpeg notes, providers
- CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, COMMUNITY
- GitHub Actions CI
- LangChain tool integration example
- Colab-oriented demo notebook

### Changed
- Repositioned project as bandwidth/privacy/cost edge layer (not “universal standard”)
- Softened marketing and paper claims; revised draft paper
- Package metadata URLs point to `Girish011/lvp-package`
- Bumped requires-python to `>=3.9`
- Provider extras now include Pillow

### Fixed
- Paper/docs no longer recommend removed FFmpeg `-vsync` (use `-fps_mode`)

## [0.1.0] - 2026-01-08

### Added
- Initial Alpha: processor, package format, CLI, Claude/OpenAI/Gemini providers
