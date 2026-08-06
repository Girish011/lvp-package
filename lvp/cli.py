"""
LVP Command Line Interface
==========================

Usage:
    lvp process video.mp4 -o video.lvp
    lvp process video.mp4 --query "What is said?" --token-budget 8000
    lvp chunk long.mp4 -o ./chunks/ --chunk-duration 600
    lvp info video.lvp
    lvp extract video.lvp -o ./extracted/
"""

import argparse
import os
import sys

from lvp import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='lvp',
        description='LVP: LLM-Ready Video Package — '
                    'edge preprocessing for bandwidth-efficient multimodal LLM input'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    process_parser = subparsers.add_parser(
        'process',
        help='Create LVP package from video'
    )
    process_parser.add_argument('video', help='Input video path')
    process_parser.add_argument(
        '-o', '--output',
        help='Output LVP path (default: same name with .lvp)'
    )
    process_parser.add_argument(
        '-p', '--profile',
        choices=['minimal', 'balanced', 'quality', 'maximum'],
        default='balanced',
        help='Device profile (default: balanced)'
    )
    process_parser.add_argument(
        '--no-transcript',
        action='store_true',
        help='Skip transcript extraction'
    )
    process_parser.add_argument(
        '-k', '--keyframes',
        type=int,
        help='Override automatic keyframe count'
    )
    process_parser.add_argument(
        '--query',
        help='Question for query-aware keyframe selection'
    )
    process_parser.add_argument(
        '--token-budget',
        type=int,
        help='Approximate vision-token budget for keyframe selection'
    )

    chunk_parser = subparsers.add_parser(
        'chunk',
        help='Split a long video into overlapping LVP packages'
    )
    chunk_parser.add_argument('video', help='Input video path')
    chunk_parser.add_argument(
        '-o', '--output-dir',
        required=True,
        help='Directory for chunk packages and manifest'
    )
    chunk_parser.add_argument(
        '--chunk-duration',
        type=float,
        default=600.0,
        help='Chunk length in seconds (default: 600)'
    )
    chunk_parser.add_argument(
        '--overlap',
        type=float,
        default=5.0,
        help='Overlap between chunks in seconds (default: 5)'
    )
    chunk_parser.add_argument(
        '-p', '--profile',
        choices=['minimal', 'balanced', 'quality', 'maximum'],
        default='balanced',
    )
    chunk_parser.add_argument('--no-transcript', action='store_true')
    chunk_parser.add_argument('--query', help='Query-aware selection per chunk')
    chunk_parser.add_argument('--token-budget', type=int)

    info_parser = subparsers.add_parser(
        'info',
        help='Show LVP package information'
    )
    info_parser.add_argument('lvp', help='LVP package path')
    info_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract LVP contents to directory'
    )
    extract_parser.add_argument('lvp', help='LVP package path')
    extract_parser.add_argument(
        '-o', '--output',
        help='Output directory (default: <name>_extracted/)'
    )

    prompt_parser = subparsers.add_parser(
        'prompt',
        help='Generate text prompt from LVP for LLMs'
    )
    prompt_parser.add_argument('lvp', help='LVP package path')

    subparsers.add_parser(
        'ffmpeg-info',
        help='Show detected FFmpeg version and LVP compatibility notes'
    )

    args = parser.parse_args()

    if args.command == 'process':
        cmd_process(args)
    elif args.command == 'chunk':
        cmd_chunk(args)
    elif args.command == 'info':
        cmd_info(args)
    elif args.command == 'extract':
        cmd_extract(args)
    elif args.command == 'prompt':
        cmd_prompt(args)
    elif args.command == 'ffmpeg-info':
        cmd_ffmpeg_info()
    else:
        parser.print_help()
        sys.exit(1)


def cmd_process(args):
    """Process a video into LVP."""
    from lvp import process

    output = args.output
    if not output:
        base = os.path.splitext(args.video)[0]
        output = f"{base}.lvp"

    print(f"Processing: {args.video}")
    print(f"Profile: {args.profile}")
    print(f"Transcript: {'disabled' if args.no_transcript else 'enabled'}")
    if args.query:
        print(f"Query-aware: {args.query}")
    if args.token_budget:
        print(f"Token budget: {args.token_budget}")
    print()

    process(
        args.video,
        output=output,
        profile=args.profile,
        transcribe=not args.no_transcript,
        target_keyframes=args.keyframes,
        query=args.query,
        token_budget=args.token_budget,
    )


def cmd_chunk(args):
    """Chunk a long video into LVP packages."""
    from lvp import process_chunked

    print(f"Chunking: {args.video}")
    print(f"Chunk duration: {args.chunk_duration}s (overlap {args.overlap}s)")
    result = process_chunked(
        args.video,
        chunk_duration=args.chunk_duration,
        overlap=args.overlap,
        output_dir=args.output_dir,
        profile=args.profile,
        transcribe=not args.no_transcript,
        query=args.query,
        token_budget=args.token_budget,
    )
    print(f"Created {len(result.chunks)} chunks in {args.output_dir}")
    print(f"Manifest: {os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.video))[0] + '_chunks.json')}")


def cmd_info(args):
    """Show LVP package info."""
    import json

    from lvp import load

    package = load(args.lvp)
    summary = package.summary()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\nLVP Package: {args.lvp}")
        print("-" * 50)
        for key, value in summary.items():
            print(f"  {key}: {value}")
        print("-" * 50)


def cmd_extract(args):
    """Extract LVP contents."""
    import zipfile

    output_dir = args.output
    if not output_dir:
        base = os.path.splitext(args.lvp)[0]
        output_dir = f"{base}_extracted"

    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(args.lvp, 'r') as lvp:
        lvp.extractall(output_dir)

    print(f"Extracted to: {output_dir}")


def cmd_prompt(args):
    """Generate text prompt from LVP."""
    from lvp import load

    package = load(args.lvp)
    print(package.to_llm_prompt())


def cmd_ffmpeg_info():
    """Print FFmpeg compatibility details."""
    from lvp.core.ffmpeg_compat import (
        MIN_RECOMMENDED,
        PREFERRED,
        check_ffmpeg_compatibility,
        has_onnx_dnn,
        has_whisper_filter,
    )

    version = check_ffmpeg_compatibility(warn=False)
    print(f"FFmpeg version: {version}")
    print(f"Recommended: >= {MIN_RECOMMENDED[0]}.{MIN_RECOMMENDED[1]}")
    print(f"Preferred:   >= {PREFERRED[0]}.{PREFERRED[1]}")
    print(f"Whisper filter available: {has_whisper_filter()}")
    print(f"ONNX/DNN filters hinted:  {has_onnx_dnn()}")
    print("Note: Do not use -vsync (removed in FFmpeg 9.0); use -fps_mode.")


if __name__ == '__main__':
    main()
