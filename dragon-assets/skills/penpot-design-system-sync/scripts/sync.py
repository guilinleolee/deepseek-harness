#!/usr/bin/env python3
"""
Penpot Design System Sync - Main CLI Script
Handles extract, transform, sync, watch, and diff commands.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync import PenpotSync
from extract import TokenExtractor
from transform import TokenTransformer
from diff import TokenDiffer


def main():
    parser = argparse.ArgumentParser(
        description="Penpot Design System Sync - Bidirectional sync between Penpot and code"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract design tokens from Penpot")
    extract_parser.add_argument("--file-id", required=True, help="Penpot file ID")
    extract_parser.add_argument("--output", default="tokens.json", help="Output file path")
    extract_parser.add_argument("--api-key", help="Penpot API key")
    extract_parser.add_argument("--api-endpoint", default="https://api.penpot.app/v1", help="Penpot API endpoint")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform tokens to target format")
    transform_parser.add_argument("--input", required=True, help="Input tokens file")
    transform_parser.add_argument("--format", required=True, choices=["json", "css", "scss", "ios", "android", "yaml", "tailwind"], help="Output format")
    transform_parser.add_argument("--output", help="Output file path (default: stdout)")
    transform_parser.add_argument("--prefix", default="", help="CSS variable prefix")
    transform_parser.add_argument("--include-semantic", action="store_true", help="Include semantic tokens")
    transform_parser.add_argument("--include-w3c", action="store_true", help="Include W3C tokens")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync tokens to multiple platforms")
    sync_parser.add_argument("--input", required=True, help="Input tokens file")
    sync_parser.add_argument("--platforms", required=True, help="Comma-separated platforms (ios,android,web,css,scss,tailwind)")
    sync_parser.add_argument("--output-dir", default="./design-system", help="Output directory")

    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Watch for design changes")
    watch_parser.add_argument("--file-id", required=True, help="Penpot file ID")
    watch_parser.add_argument("--on-change", required=True, help="Command to run on change")
    watch_parser.add_argument("--api-key", help="Penpot API key")
    watch_parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds")

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Compare two token versions")
    diff_parser.add_argument("--before", required=True, help="Before tokens file")
    diff_parser.add_argument("--after", required=True, help="After tokens file")
    diff_parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    if args.command == "extract":
        handle_extract(args)
    elif args.command == "transform":
        handle_transform(args)
    elif args.command == "sync":
        handle_sync(args)
    elif args.command == "watch":
        handle_watch(args)
    elif args.command == "diff":
        handle_diff(args)
    else:
        parser.print_help()
        sys.exit(1)


def handle_extract(args):
    """Extract design tokens from Penpot."""
    sync = PenpotSync(
        api_key=args.api_key,
        api_endpoint=args.api_endpoint
    )

    tokens = sync.extract_tokens(file_id=args.file_id)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(tokens.get('colors', []))} colors, "
          f"{len(tokens.get('typography', []))} typography, "
          f"{len(tokens.get('spacing', []))} spacing, "
          f"{len(tokens.get('shadows', []))} shadows to {args.output}")


def handle_transform(args):
    """Transform tokens to target format."""
    with open(args.input, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    transformer = TokenTransformer(tokens)
    options = {
        "prefix": args.prefix,
        "includeSemantic": args.include_semantic,
        "includeW3C": args.include_w3c
    }

    result = transformer.transform(args.format, options)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Transformed to {args.format} format: {args.output}")
    else:
        print(result)


def handle_sync(args):
    """Sync tokens to multiple platforms."""
    with open(args.input, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    platforms = [p.strip() for p in args.platforms.split(",")]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sync = PenpotSync()
    results = sync.export(tokens, formats=platforms, output_dir=str(output_dir))

    for platform, content in results.items():
        print(f"Generated {platform}: {output_dir / platform}")


def handle_watch(args):
    """Watch for design changes and trigger callback."""
    import time
    import subprocess

    sync = PenpotSync(
        api_key=args.api_key,
        api_endpoint=args.api_endpoint
    )

    last_hash = None

    print(f"Watching file {args.file_id} for changes (interval: {args.interval}s)")
    print(f"Callback: {args.on_change}")

    while True:
        try:
            tokens = sync.extract_tokens(file_id=args.file_id)
            current_hash = hash(json.dumps(tokens, sort_keys=True))

            if last_hash and current_hash != last_hash:
                print(f"\n[CHANGE DETECTED] Design tokens updated!")
                print(f"Running callback: {args.on_change}")

                # Run the callback command
                result = subprocess.run(
                    args.on_change,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

            last_hash = current_hash
            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\nStopping watch...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(args.interval)


def handle_diff(args):
    """Compare two token versions."""
    differ = TokenDiffer()
    result = differ.compare(args.before, args.after)

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Diff report written to {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
