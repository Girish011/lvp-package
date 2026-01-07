"""
LVP Providers
=============

Integration with various LLM providers (Claude, GPT-4V, Gemini, etc.)
"""

import os
import base64
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from lvp.core.package import LVPPackage


class LLMProvider(ABC):
    """
    Base class for LLM provider integrations.
    
    Subclass this to add support for new providers.
    """
    
    @abstractmethod
    def query(
        self, 
        package: LVPPackage, 
        question: str,
        **kwargs
    ) -> str:
        """
        Query the LLM with an LVP package.
        
        Args:
            package: LVPPackage to analyze
            question: Question or instruction for the LLM
            **kwargs: Provider-specific options
            
        Returns:
            LLM response text
        """
        pass
    
    def _prepare_keyframes_base64(
        self, 
        package: LVPPackage,
        max_images: int = 20
    ) -> List[str]:
        """Convert keyframes to base64 for API upload."""
        keyframes = package.get_keyframes()
        
        # Limit number of images if needed
        if len(keyframes) > max_images:
            step = len(keyframes) // max_images
            keyframes = keyframes[::step][:max_images]
        
        return [
            base64.b64encode(kf).decode('utf-8')
            for kf in keyframes
        ]
    
    def _build_context(self, package: LVPPackage) -> str:
        """Build context string from package metadata."""
        parts = [
            f"Video: {package.source_filename}",
            f"Duration: {package.source_duration:.1f} seconds",
            f"Keyframes shown: {package.keyframe_count}",
        ]
        
        if package.has_transcript:
            parts.append(f"\nTranscript:\n{package.transcript}")
        
        return "\n".join(parts)


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude integration.
    
    Requires: pip install anthropic
    
    Example:
        >>> from lvp.providers import ClaudeProvider
        >>> claude = ClaudeProvider(api_key="sk-...")
        >>> response = claude.query(package, "What happens in this video?")
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-sonnet-4-20250514)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set ANTHROPIC_API_KEY"
            )
    
    def query(
        self,
        package: LVPPackage,
        question: str,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Query Claude with an LVP package.
        
        Args:
            package: LVPPackage to analyze
            question: Question about the video
            max_tokens: Maximum response length
            
        Returns:
            Claude's response
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # Prepare images
        keyframes_b64 = self._prepare_keyframes_base64(package)
        
        # Build message content
        content = []
        
        # Add context
        context = self._build_context(package)
        content.append({
            "type": "text",
            "text": f"I'm sharing keyframes from a video for analysis.\n\n{context}\n\nKeyframes:"
        })
        
        # Add images
        for b64_data in keyframes_b64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/webp",
                    "data": b64_data
                }
            })
        
        # Add question
        content.append({
            "type": "text",
            "text": f"\nQuestion: {question}"
        })
        
        # Make request
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": content
            }]
        )
        
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT-4V integration.
    
    Requires: pip install openai
    
    Example:
        >>> from lvp.providers import OpenAIProvider
        >>> gpt = OpenAIProvider(api_key="sk-...")
        >>> response = gpt.query(package, "What happens in this video?")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o)
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set OPENAI_API_KEY"
            )
    
    def query(
        self,
        package: LVPPackage,
        question: str,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Query GPT-4V with an LVP package."""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )
        
        client = openai.OpenAI(api_key=self.api_key)
        
        # Prepare images
        keyframes_b64 = self._prepare_keyframes_base64(package)
        
        # Build message content
        content = []
        
        # Add context
        context = self._build_context(package)
        content.append({
            "type": "text",
            "text": f"I'm sharing keyframes from a video for analysis.\n\n{context}\n\nKeyframes:"
        })
        
        # Add images
        for b64_data in keyframes_b64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/webp;base64,{b64_data}"
                }
            })
        
        # Add question
        content.append({
            "type": "text",
            "text": f"\nQuestion: {question}"
        })
        
        # Make request
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": content
            }]
        )
        
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    """
    Google Gemini integration.
    
    Requires: pip install google-generativeai
    
    Example:
        >>> from lvp.providers import GeminiProvider
        >>> gemini = GeminiProvider(api_key="...")
        >>> response = gemini.query(package, "What happens in this video?")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash"
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env var)
            model: Model to use (default: gemini-1.5-flash)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set GOOGLE_API_KEY"
            )
    
    def query(
        self,
        package: LVPPackage,
        question: str,
        **kwargs
    ) -> str:
        """Query Gemini with an LVP package."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai required. Install with: "
                "pip install google-generativeai"
            )
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        
        # Prepare content
        keyframes = package.get_keyframes()
        
        # Limit keyframes for Gemini
        if len(keyframes) > 16:
            step = len(keyframes) // 16
            keyframes = keyframes[::step][:16]
        
        # Build parts
        parts = []
        
        # Add context
        context = self._build_context(package)
        parts.append(f"I'm sharing keyframes from a video for analysis.\n\n{context}\n\nKeyframes:")
        
        # Add images
        for kf_data in keyframes:
            parts.append({
                'mime_type': 'image/webp',
                'data': kf_data
            })
        
        # Add question
        parts.append(f"\nQuestion: {question}")
        
        # Make request
        response = model.generate_content(parts)
        
        return response.text


# Export all providers
__all__ = [
    'LLMProvider',
    'ClaudeProvider', 
    'OpenAIProvider',
    'GeminiProvider'
]
