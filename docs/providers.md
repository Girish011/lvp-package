# LLM providers

LVP sends **WebP keyframes as images** plus optional transcript text.

| Provider | Extra | Env var | Default model |
|----------|-------|---------|---------------|
| OpenAI | `pip install -e ".[openai]"` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `pip install -e ".[claude]"` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google | `pip install -e ".[gemini]"` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| DeepSeek | `pip install -e ".[deepseek]"` | `DEEPSEEK_API_KEY` | `deepseek-v4-pro` |

```python
from lvp.providers import OpenAIProvider, ClaudeProvider, GeminiProvider

package = lvp.load("video.lvp")
print(OpenAIProvider().query(package, "Summarize this video."))
```

## Native video APIs

Gemini Files / Claude video can accept raw video. That path is **out of band** for `.lvp` packages. Use `benchmarks/run_comparison.py --include-native-stub` as a starting point and implement upload in your eval harness for fair comparisons.

## LangChain

See `examples/langchain_example.py` and `lvp.integrations.langchain_tool`.
