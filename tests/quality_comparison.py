"""
LVP Quality Comparison Script
=============================

Compares LLM responses between:
- Raw video upload (baseline)
- LVP package (our method)

Usage:
    python quality_comparison.py video.mp4 --provider claude --api-key YOUR_KEY

Output:
    - Comparison results in JSON
    - Summary statistics
    - CSV for paper/analysis
"""

import argparse
import base64
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Optional

import lvp

# Test questions for comparison
TEST_QUESTIONS = [
    "What is happening in this video?",
    "Describe the main objects or people visible.",
    "What is the setting or environment?",
    "Summarize this video in one sentence.",
]


@dataclass
class ComparisonResult:
    """Single question comparison result."""
    question: str
    raw_response: str
    lvp_response: str
    raw_tokens: int
    lvp_tokens: int
    semantic_similarity: float
    key_facts_raw: List[str]
    key_facts_lvp: List[str]
    fact_overlap: float
    llm_judge_score: Optional[float]  # 1-5 scale
    llm_judge_reasoning: Optional[str]


@dataclass 
class VideoComparisonReport:
    """Full comparison report for one video."""
    video_file: str
    video_size_bytes: int
    lvp_size_bytes: int
    compression_ratio: float
    provider: str
    timestamp: str
    questions: List[ComparisonResult]
    average_similarity: float
    average_fact_overlap: float
    average_judge_score: Optional[float]


class QualityComparison:
    """Compare LVP vs raw video quality."""
    
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self._setup_provider()
    
    def _setup_provider(self):
        """Initialize the LLM provider."""
        if self.provider == "claude":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.model = "claude-sonnet-4-20250514"
            except ImportError:
                raise ImportError("pip install anthropic")
                
        elif self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                self.model = "gpt-4o"
            except ImportError:
                raise ImportError("pip install openai")
                
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
                self.model = "gemini-3-flash-preview"
            except ImportError:
                raise ImportError("pip install google-generativeai")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _query_raw_video(self, video_path: str, question: str) -> str:
        """Query LLM with raw video file."""
        
        # Read video as base64
        with open(video_path, "rb") as f:
            video_data = base64.standard_b64encode(f.read()).decode("utf-8")
        
        # Get mime type
        ext = os.path.splitext(video_path)[1].lower()
        mime_types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".webm": "video/webm",
        }
        mime_type = mime_types.get(ext, "video/mp4")
        
        if self.provider == "claude":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "video",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": video_data,
                            }
                        },
                        {"type": "text", "text": question}
                    ]
                }]
            )
            return response.content[0].text
            
        elif self.provider == "openai":
            # OpenAI doesn't support video directly, use frames
            # For fair comparison, extract same keyframes
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": f"data:{mime_type};base64,{video_data}"
                            }
                        },
                        {"type": "text", "text": question}
                    ]
                }]
            )
            return response.choices[0].message.content
            
        elif self.provider == "gemini":
            # Gemini needs file upload
            video_file = self.client.upload_file(video_path)
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content([video_file, question])
            return response.text
    
    def _query_lvp(self, package: lvp.LVPPackage, question: str) -> str:
        """Query LLM with LVP package."""
        
        # Get keyframes as base64
        keyframes = package.get_keyframes()
        
        if self.provider == "claude":
            content = []
            
            # Add keyframes
            for i, kf in enumerate(keyframes):
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/webp",
                        "data": base64.standard_b64encode(kf).decode("utf-8"),
                    }
                })
            
            # Add transcript if available
            if package.has_transcript:
                content.append({
                    "type": "text",
                    "text": f"[Transcript]: {package.transcript}"
                })
            
            # Add question
            content.append({"type": "text", "text": question})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": content}]
            )
            return response.content[0].text
            
        elif self.provider == "openai":
            content = []
            
            for kf in keyframes:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/webp;base64,{base64.standard_b64encode(kf).decode('utf-8')}"
                    }
                })
            
            if package.has_transcript:
                content.append({
                    "type": "text",
                    "text": f"[Transcript]: {package.transcript}"
                })
            
            content.append({"type": "text", "text": question})
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": content}]
            )
            return response.choices[0].message.content
            
        elif self.provider == "gemini":
            import io

            import PIL.Image
            
            parts = []
            
            for kf in keyframes:
                img = PIL.Image.open(io.BytesIO(kf))
                parts.append(img)
            
            if package.has_transcript:
                parts.append(f"[Transcript]: {package.transcript}")
            
            parts.append(question)
            
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(parts)
            return response.text
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        
        # Simple word overlap (Jaccard similarity)
        # For production, use sentence-transformers
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts/entities from response."""
        
        # Simple extraction - look for nouns/objects
        # For production, use NER or ask LLM to extract
        import re
        
        # Remove common words
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
            'until', 'while', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'whom', 'its', 'his', 'her', 'their', 'our', 'your',
            'video', 'image', 'shows', 'appears', 'seems', 'looks',
            'visible', 'see', 'seen', 'show', 'showing', 'displayed',
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        facts = [w for w in words if w not in stopwords]
        
        # Return unique facts
        return list(dict.fromkeys(facts))[:20]
    
    def _llm_judge(self, question: str, raw_response: str, lvp_response: str) -> tuple:
        """Use LLM to judge response quality."""
        
        judge_prompt = f"""You are evaluating two AI responses to the same question about a video.

Question: {question}

Response A (from raw video):
{raw_response}

Response B (from compressed package):
{lvp_response}

Rate how well Response B captures the same information as Response A on a scale of 1-5:
1 = Completely different, missing most information
2 = Somewhat different, missing key details  
3 = Similar, captures main points but missing some details
4 = Very similar, captures almost all information
5 = Equivalent, no meaningful difference

Respond with JSON only:
{{"score": <1-5>, "reasoning": "<brief explanation>"}}"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=256,
                    messages=[{"role": "user", "content": judge_prompt}]
                )
                result = json.loads(response.content[0].text)
                
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Use cheaper model for judging
                    max_tokens=256,
                    messages=[{"role": "user", "content": judge_prompt}]
                )
                result = json.loads(response.choices[0].message.content)
                
            elif self.provider == "gemini":
                model = self.client.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(judge_prompt)
                result = json.loads(response.text)
            
            return result.get("score", 3), result.get("reasoning", "")
            
        except Exception as e:
            print(f"  Warning: LLM judge failed: {e}")
            return None, None
    
    def compare(
        self, 
        video_path: str, 
        questions: List[str] = None,
        include_judge: bool = True
    ) -> VideoComparisonReport:
        """Run full comparison on a video."""
        
        if questions is None:
            questions = TEST_QUESTIONS
        
        print(f"\n{'='*60}")
        print(f"Quality Comparison: {os.path.basename(video_path)}")
        print(f"{'='*60}")
        
        # Get video size
        video_size = os.path.getsize(video_path)
        print(f"Video size: {video_size / 1024:.1f} KB")
        
        # Create LVP package
        print("Creating LVP package...")
        package = lvp.process(video_path)
        
        # Save temporarily to get size
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".lvp", delete=False) as f:
            temp_lvp = f.name
        package.save(temp_lvp)
        lvp_size = os.path.getsize(temp_lvp)
        os.unlink(temp_lvp)
        
        compression = video_size / lvp_size
        print(f"LVP size: {lvp_size / 1024:.1f} KB (compression: {compression:.1f}x)")
        
        # Run comparisons
        results = []
        
        for i, question in enumerate(questions):
            print(f"\nQuestion {i+1}/{len(questions)}: {question[:50]}...")
            
            # Query raw video
            print("  Querying with raw video...")
            try:
                raw_response = self._query_raw_video(video_path, question)
            except Exception as e:
                print(f"  Error with raw video: {e}")
                raw_response = f"[Error: {e}]"
            
            # Query LVP
            print("  Querying with LVP package...")
            try:
                lvp_response = self._query_lvp(package, question)
            except Exception as e:
                print(f"  Error with LVP: {e}")
                lvp_response = f"[Error: {e}]"
            
            # Compute metrics
            similarity = self._compute_similarity(raw_response, lvp_response)
            facts_raw = self._extract_key_facts(raw_response)
            facts_lvp = self._extract_key_facts(lvp_response)
            
            fact_overlap = len(set(facts_raw) & set(facts_lvp)) / max(len(facts_raw), 1)
            
            # LLM judge
            judge_score, judge_reasoning = None, None
            if include_judge:
                print("  Running LLM judge...")
                judge_score, judge_reasoning = self._llm_judge(
                    question, raw_response, lvp_response
                )
            
            result = ComparisonResult(
                question=question,
                raw_response=raw_response,
                lvp_response=lvp_response,
                raw_tokens=len(raw_response.split()),
                lvp_tokens=len(lvp_response.split()),
                semantic_similarity=similarity,
                key_facts_raw=facts_raw,
                key_facts_lvp=facts_lvp,
                fact_overlap=fact_overlap,
                llm_judge_score=judge_score,
                llm_judge_reasoning=judge_reasoning,
            )
            results.append(result)
            
            print(f"  Similarity: {similarity:.2%}")
            print(f"  Fact overlap: {fact_overlap:.2%}")
            if judge_score:
                print(f"  Judge score: {judge_score}/5")
        
        # Compute averages
        avg_similarity = sum(r.semantic_similarity for r in results) / len(results)
        avg_fact_overlap = sum(r.fact_overlap for r in results) / len(results)
        
        judge_scores = [r.llm_judge_score for r in results if r.llm_judge_score]
        avg_judge = sum(judge_scores) / len(judge_scores) if judge_scores else None
        
        report = VideoComparisonReport(
            video_file=os.path.basename(video_path),
            video_size_bytes=video_size,
            lvp_size_bytes=lvp_size,
            compression_ratio=compression,
            provider=self.provider,
            timestamp=datetime.now().isoformat(),
            questions=results,
            average_similarity=avg_similarity,
            average_fact_overlap=avg_fact_overlap,
            average_judge_score=avg_judge,
        )
        
        return report


def print_report(report: VideoComparisonReport):
    """Print formatted report."""
    
    print(f"\n{'='*60}")
    print("COMPARISON REPORT")
    print(f"{'='*60}")
    print(f"Video: {report.video_file}")
    print(f"Provider: {report.provider}")
    print(f"Compression: {report.compression_ratio:.1f}x")
    print(f"  Original: {report.video_size_bytes / 1024:.1f} KB")
    print(f"  LVP: {report.lvp_size_bytes / 1024:.1f} KB")
    
    print(f"\n{'─'*60}")
    print("QUALITY METRICS")
    print(f"{'─'*60}")
    print(f"Average Semantic Similarity: {report.average_similarity:.1%}")
    print(f"Average Fact Overlap: {report.average_fact_overlap:.1%}")
    if report.average_judge_score:
        print(f"Average LLM Judge Score: {report.average_judge_score:.1f}/5")
    
    print(f"\n{'─'*60}")
    print("PER-QUESTION RESULTS")
    print(f"{'─'*60}")
    
    for i, r in enumerate(report.questions):
        print(f"\nQ{i+1}: {r.question}")
        print(f"  Similarity: {r.semantic_similarity:.1%}")
        print(f"  Fact overlap: {r.fact_overlap:.1%}")
        if r.llm_judge_score:
            print(f"  Judge: {r.llm_judge_score}/5 - {r.llm_judge_reasoning}")
        print(f"  Raw response ({r.raw_tokens} words): {r.raw_response[:100]}...")
        print(f"  LVP response ({r.lvp_tokens} words): {r.lvp_response[:100]}...")


def save_report(report: VideoComparisonReport, output_path: str):
    """Save report to JSON."""
    
    # Convert to dict
    data = {
        "video_file": report.video_file,
        "video_size_bytes": report.video_size_bytes,
        "lvp_size_bytes": report.lvp_size_bytes,
        "compression_ratio": report.compression_ratio,
        "provider": report.provider,
        "timestamp": report.timestamp,
        "average_similarity": report.average_similarity,
        "average_fact_overlap": report.average_fact_overlap,
        "average_judge_score": report.average_judge_score,
        "questions": [asdict(q) for q in report.questions],
    }
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nReport saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare LVP vs raw video quality"
    )
    parser.add_argument("video", help="Path to video file")
    parser.add_argument(
        "--provider", 
        choices=["claude", "openai", "gemini"],
        default="claude",
        help="LLM provider (default: claude)"
    )
    parser.add_argument("--api-key", required=True, help="API key")
    parser.add_argument(
        "--output", "-o",
        default="comparison_report.json",
        help="Output JSON file"
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip LLM-as-judge evaluation"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video not found: {args.video}")
        return 1
    
    # Run comparison
    comparator = QualityComparison(args.provider, args.api_key)
    report = comparator.compare(
        args.video,
        include_judge=not args.no_judge
    )
    
    # Print and save
    print_report(report)
    save_report(report, args.output)
    
    # Summary for paper
    print(f"\n{'='*60}")
    print("SUMMARY FOR PAPER")
    print(f"{'='*60}")
    print(f"Compression: {report.compression_ratio:.1f}x")
    print(f"Quality retention: {report.average_similarity * 100:.1f}%")
    if report.average_judge_score:
        print(f"LLM judge: {report.average_judge_score:.1f}/5 ({report.average_judge_score/5*100:.0f}%)")
    
    return 0


if __name__ == "__main__":
    exit(main())
