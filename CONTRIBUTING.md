# Contributing to LVP

Thanks for your interest in improving LVP.

## Development setup

```bash
git clone https://github.com/Girish011/lvp-package.git
cd lvp-package
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

FFmpeg 8.0+ must be on `PATH` (`lvp ffmpeg-info` to verify).

## Tests

```bash
pytest tests/ -q
```

CI runs lint (ruff) + pytest. Prefer unit tests that use the generated fixture in `tests/conftest.py` rather than large personal videos.

## Code style

- Python 3.9+
- `ruff check lvp tests`
- Keep PRs focused; match existing naming and module layout

## Pull requests

1. Open an issue for larger features when possible
2. Branch from `master`
3. Include tests for behavior changes
4. Update docs/CHANGELOG for user-facing changes
5. Do not commit API keys, `.env`, or large binary datasets

## Good first contributions

- Provider adapters / model ID updates
- Additional device profiles
- Benchmark scripts for a new stress category
- Docs clarifications and examples

## Code of conduct

By participating you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).
