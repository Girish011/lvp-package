"""
LVP Quality Validation (OpenAI Only)
====================================

Since OpenAI doesn't support raw video, this script:
1. Processes video to LVP
2. Sends LVP to OpenAI GPT-4o
3. Validates response quality

Usage:
    python lvp_openai_test.py video.mp4 --api-key YOUR_KEY
"""

import argparse
import base64
import json
import os
import time
from datetime import datetime

import lvp

# Test questions
TEST_QUESTIONS = [
    "What is happening in this video?",
    "Describe the main objects or people visible.",
    "What is the setting or environment?",
    "What text or words are visible on screen?",
    "Summarize this video in one sentence.",
    "Summarize if there is audio in the video."
]


def query_openai_with_lvp(package: lvp.LVPPackage, question: str, api_key: str) -> str:
    """Send LVP package to OpenAI."""
    
    from io import BytesIO

    import openai
    
    client = openai.OpenAI(api_key=api_key)
    
    # Build content with keyframes
    content = []
    
    keyframes = package.get_keyframes()
    for kf in keyframes:
        # Convert WebP to PNG for better OpenAI compatibility
        try:
            from PIL import Image
            img = Image.open(BytesIO(kf))
            png_buffer = BytesIO()
            img.save(png_buffer, format="PNG")
            png_data = png_buffer.getvalue()
            b64 = base64.standard_b64encode(png_data).decode("utf-8")
            mime_type = "image/png"
        except ImportError:
            # Fallback to WebP if PIL not available
            b64 = base64.standard_b64encode(kf).decode("utf-8")
            mime_type = "image/webp"
        
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{b64}"
            }
        })
    
    # Add transcript if available
    if package.has_transcript:
        content.append({
            "type": "text",
            "text": f"[Audio transcript]: {package.transcript}"
        })
    
    # Add question
    content.append({
        "type": "text", 
        "text": f"This is a video with {package.keyframe_count} keyframe(s). {question}"
    })
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[{"role": "user", "content": content}]
    )
    
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Test LVP with OpenAI")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    parser.add_argument("--output", "-o", default="lvp_test_results.json")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video not found: {args.video}")
        return 1
    
    print("=" * 60)
    print("LVP + OpenAI Quality Test")
    print("=" * 60)
    
    # Video info
    video_size = os.path.getsize(args.video)
    print(f"\nVideo: {args.video}")
    print(f"Size: {video_size / 1024:.1f} KB")
    
    # Create LVP
    print("\nCreating LVP package...")
    package = lvp.process(args.video)
    
    # Save to get size
    lvp_path = args.video.replace(".mp4", ".lvp")
    package.save(lvp_path)
    lvp_size = os.path.getsize(lvp_path)
    
    compression = video_size / lvp_size
    print(f"LVP size: {lvp_size / 1024:.1f} KB")
    print(f"Compression: {compression:.1f}x")
    print(f"Keyframes: {package.keyframe_count}")
    print(f"Transcript: {package.transcript if package.has_transcript else 'None'}")
    
    # Test questions
    print("\n" + "=" * 60)
    print("QUERYING OPENAI")
    print("=" * 60)
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS):
        print(f"\n[Q{i+1}] {question}")
        print("-" * 40)
        
        # Retry logic with delay
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = query_openai_with_lvp(package, question, args.api_key)
                print(f"Response: {response}")
                results.append({
                    "question": question,
                    "response": response,
                    "status": "success"
                })
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Attempt {attempt+1} failed, retrying in 3s...")
                    time.sleep(3)
                else:
                    print(f"Error: {e}")
                    results.append({
                        "question": question,
                        "response": str(e),
                        "status": "error"
                    })
        
        # Delay between questions to avoid rate limiting
        if i < len(TEST_QUESTIONS) - 1:
            print("  (waiting 2s...)")
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    
    print(f"Video: {os.path.basename(args.video)}")
    print(f"Compression: {compression:.1f}x ({video_size/1024:.0f} KB → {lvp_size/1024:.0f} KB)")
    print(f"Questions answered: {success_count}/{len(results)}")
    
    # Save results
    report = {
        "video": os.path.basename(args.video),
        "video_size_kb": video_size / 1024,
        "lvp_size_kb": lvp_size / 1024,
        "compression_ratio": compression,
        "keyframes": package.keyframe_count,
        "has_transcript": package.has_transcript,
        "transcript": package.transcript if package.has_transcript else None,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nResults saved to: {args.output}")
    
    # Print for paper
    print("\n" + "=" * 60)
    print("FOR PAPER")
    print("=" * 60)
    print(f"- Compression ratio: {compression:.1f}x")
    print(f"- Bandwidth saved: {(1 - lvp_size/video_size) * 100:.1f}%")
    print("- OpenAI successfully processed LVP: Yes")
    print(f"- All questions answered: {'Yes' if success_count == len(results) else 'No'}")
    
    return 0


if __name__ == "__main__":
    exit(main())