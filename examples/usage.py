"""
LVP Examples
============

This file demonstrates various ways to use the LVP library.
"""

# =============================================================================
# Example 1: Basic Processing
# =============================================================================

import lvp

# Process a video with default settings
package = lvp.process("my_video.mp4")

# Save to file
package.save("my_video.lvp")

# Check compression stats
print(package.summary())


# =============================================================================
# Example 2: Custom Profile
# =============================================================================

# Use minimal profile for slow connections
package = lvp.process(
    "my_video.mp4",
    profile="minimal",      # Fewer keyframes, smaller resolution
    transcribe=False        # Skip transcription for faster processing
)

# Use maximum quality for detailed analysis
package = lvp.process(
    "my_video.mp4",
    profile="maximum",
    target_keyframes=50     # Override to get more keyframes
)


# =============================================================================
# Example 3: Loading and Inspecting
# =============================================================================

# Load existing LVP file
package = lvp.load("my_video.lvp")

# Get summary
print(package.summary())

# Get transcript
print(package.transcript)

# Get keyframe count
print(f"Keyframes: {package.keyframe_count}")

# Get individual keyframe as bytes
keyframe_data = package.get_keyframe(0)

# Get all keyframes
all_keyframes = package.get_keyframes()


# =============================================================================
# Example 4: Query Claude
# =============================================================================

from lvp.providers import ClaudeProvider

# Initialize provider
claude = ClaudeProvider(api_key="your-api-key")
# Or set ANTHROPIC_API_KEY environment variable

# Load package and query
package = lvp.load("my_video.lvp")
response = claude.query(package, "What is the main topic of this video?")
print(response)

# More detailed query
response = claude.query(
    package, 
    "Please provide a detailed timeline of events in this video."
)


# =============================================================================
# Example 5: Query OpenAI GPT-4V
# =============================================================================

from lvp.providers import OpenAIProvider

gpt = OpenAIProvider(api_key="your-api-key")
# Or set OPENAI_API_KEY environment variable

package = lvp.load("my_video.lvp")
response = gpt.query(package, "Describe what happens in this video.")
print(response)


# =============================================================================
# Example 6: Query Google Gemini
# =============================================================================

from lvp.providers import GeminiProvider

gemini = GeminiProvider(api_key="your-api-key")
# Or set GOOGLE_API_KEY environment variable

package = lvp.load("my_video.lvp")
response = gemini.query(package, "Summarize this video in 3 bullet points.")
print(response)


# =============================================================================
# Example 7: Cross-Provider Comparison
# =============================================================================

from lvp.providers import ClaudeProvider, OpenAIProvider, GeminiProvider

package = lvp.load("my_video.lvp")
question = "What is the main message of this video?"

providers = [
    ("Claude", ClaudeProvider()),
    ("GPT-4V", OpenAIProvider()),
    ("Gemini", GeminiProvider()),
]

for name, provider in providers:
    try:
        response = provider.query(package, question)
        print(f"\n{name}:\n{response[:500]}...")
    except Exception as e:
        print(f"\n{name}: Error - {e}")


# =============================================================================
# Example 8: Text-Only Fallback
# =============================================================================

# Generate a text prompt when vision API isn't available
package = lvp.load("my_video.lvp")
text_prompt = package.to_llm_prompt()
print(text_prompt)

# This can be sent to any text-only LLM for basic understanding


# =============================================================================
# Example 9: Batch Processing
# =============================================================================

import os
from pathlib import Path

video_dir = Path("./videos")
output_dir = Path("./lvp_packages")
output_dir.mkdir(exist_ok=True)

for video_file in video_dir.glob("*.mp4"):
    print(f"Processing: {video_file.name}")
    package = lvp.process(str(video_file))
    output_path = output_dir / f"{video_file.stem}.lvp"
    package.save(str(output_path))
    print(f"  → {output_path} ({package.summary()['compression_ratio']}x compression)")


# =============================================================================
# Example 10: Integration with Web App
# =============================================================================

# Flask example
"""
from flask import Flask, request, jsonify
import lvp
from lvp.providers import ClaudeProvider

app = Flask(__name__)
claude = ClaudeProvider()

@app.route('/analyze', methods=['POST'])
def analyze_video():
    # Receive uploaded video
    video = request.files['video']
    video_path = f"/tmp/{video.filename}"
    video.save(video_path)
    
    # Process to LVP
    package = lvp.process(video_path, profile='balanced')
    
    # Query LLM
    question = request.form.get('question', 'What happens in this video?')
    response = claude.query(package, question)
    
    return jsonify({
        'response': response,
        'compression': package.summary()['compression_ratio']
    })
"""

print("Examples loaded. See source code for usage patterns.")
