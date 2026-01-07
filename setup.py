"""
LVP: LLM-Ready Video Package
============================

A universal standard for bandwidth-efficient video upload to multimodal LLMs.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lvp",
    version="0.1.0",
    author="LVP Research Partnership",
    author_email="lvp-research@example.com",
    description="A universal standard for bandwidth-efficient video upload to multimodal LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lvp-research/lvp",
    project_urls={
        "Bug Tracker": "https://github.com/lvp-research/lvp/issues",
        "Documentation": "https://github.com/lvp-research/lvp#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies only - providers are optional
    ],
    extras_require={
        "whisper": ["openai-whisper"],
        "claude": ["anthropic"],
        "openai": ["openai"],
        "gemini": ["google-generativeai"],
        "all": [
            "openai-whisper",
            "anthropic",
            "openai", 
            "google-generativeai",
        ],
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "lvp=lvp.cli:main",
        ],
    },
)
