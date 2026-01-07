"""
LVP Command Line Interface
==========================

Usage:
    lvp process video.mp4 -o video.lvp
    lvp info video.lvp
    lvp extract video.lvp -o ./extracted/
"""

import argparse
import sys
import os


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='lvp',
        description='LVP: LLM-Ready Video Package - '
                    'Bandwidth-efficient video preprocessing for multimodal LLMs'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.1.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
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
    
    # Info command
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
    
    # Extract command
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract LVP contents to directory'
    )
    extract_parser.add_argument('lvp', help='LVP package path')
    extract_parser.add_argument(
        '-o', '--output',
        help='Output directory (default: <name>_extracted/)'
    )
    
    # Prompt command
    prompt_parser = subparsers.add_parser(
        'prompt',
        help='Generate text prompt from LVP for LLMs'
    )
    prompt_parser.add_argument('lvp', help='LVP package path')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        cmd_process(args)
    elif args.command == 'info':
        cmd_info(args)
    elif args.command == 'extract':
        cmd_extract(args)
    elif args.command == 'prompt':
        cmd_prompt(args)
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
    print()
    
    package = process(
        args.video,
        output=output,
        profile=args.profile,
        transcribe=not args.no_transcript,
        target_keyframes=args.keyframes
    )


def cmd_info(args):
    """Show LVP package info."""
    from lvp import load
    import json
    
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


if __name__ == '__main__':
    main()
