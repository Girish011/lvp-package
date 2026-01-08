import lvp
import os

# 1. Process
print("Processing video...")
pkg = lvp.process("uploads/test_audio_video.mp4")  # Replace with your video

# 2. Save
pkg.save("uploads/test_audio_video.lvp")

# 3. Verify ZIP has keyframes
import zipfile
with zipfile.ZipFile("uploads/test_audio_video.lvp") as z:
    kf_count = len([f for f in z.namelist() if "keyframe" in f])
    print(f"✓ Keyframes in ZIP: {kf_count}")

# 4. Load and verify
loaded = lvp.load("uploads/test_audio_video.lvp")
print(f"✓ Loaded keyframes: {len(loaded.get_keyframes())}")
print(f"✓ Summary: {loaded.summary()}")

# 5. Test provider (optional - uncomment one)
from lvp.providers import OpenAIProvider
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    response = OpenAIProvider(api_key=api_key).query(loaded, "What is shown in this video?")
    print(response)
else:
    print("⚠️  OPENAI_API_KEY environment variable not set. Skipping provider test.")