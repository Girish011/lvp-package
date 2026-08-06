"""
LVP Examples — concise patterns (see also colab_demo.ipynb, langchain_example.py).
"""

# =============================================================================
# Basic processing
# =============================================================================

import lvp

package = lvp.process("my_video.mp4", profile="balanced")
package.save("my_video.lvp")
print(package.summary())

# =============================================================================
# Query-aware + token budget
# =============================================================================

package = lvp.process(
    "talk.mp4",
    query="What is the speaker's conclusion?",
    token_budget=8000,
    profile="quality",
)

# =============================================================================
# Long video chunking
# =============================================================================

result = lvp.process_chunked(
    "hour_long.mp4",
    chunk_duration=600,
    overlap=10,
    output_dir="./chunks",
)
print(result.to_manifest()["chunk_count"])

# =============================================================================
# Load + provider query
# =============================================================================

from lvp.providers import OpenAIProvider, ClaudeProvider, GeminiProvider

package = lvp.load("my_video.lvp")
# response = OpenAIProvider().query(package, "Summarize this video.")

# =============================================================================
# LangChain tool
# =============================================================================

# from lvp.integrations import as_langchain_tool
# tool = as_langchain_tool()
