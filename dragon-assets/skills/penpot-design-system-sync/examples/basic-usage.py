#!/usr/bin/env python3
"""
penpot-design-system-sync - Basic Usage Example

This script demonstrates the core workflows for extracting design tokens
from Penpot and transforming them to various output formats.
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from penpot_sync import PenpotSync


def demo_extract_tokens():
    """Extract tokens from Penpot file and save to JSON."""
    print("\n" + "=" * 60)
    print("DEMO 1: Extract Tokens from Penpot")
    print("=" * 60)

    # Initialize sync (use env var PENPOT_API_KEY or pass directly)
    api_key = os.getenv("PENPOT_API_KEY")
    penpot_url = os.getenv("PENPOT_URL", "https://penpot.app")

    if not api_key:
        print("⚠️  PENPOT_API_KEY not set - using mock data for demo")
        # Use mock data for demonstration
        mock_tokens = {
            "colors": {
                "primary": {"value": "#3b82f6", "type": "color"},
                "secondary": {"value": "#6b7280", "type": "color"},
                "accent": {"value": "#f59e0b", "type": "color"},
            },
            "typography": {
                "fontFamily": {"value": "Inter, sans-serif", "type": "fontFamily"},
                "fontSize": {"value": "16px", "type": "fontSize"},
                "fontWeight": {"value": "400", "type": "fontWeight"},
            },
            "spacing": {
                "sm": {"value": "8px", "type": "dimension"},
                "md": {"value": "16px", "type": "dimension"},
                "lg": {"value": "24px", "type": "dimension"},
            },
        }

        # Save mock tokens
        output_file = Path(__file__).parent.parent / "tokens.json"
        with open(output_file, "w") as f:
            json.dump(mock_tokens, f, indent=2)
        print(f"✓ Mock tokens saved to: {output_file}")
        return output_file

    # Real extraction
    sync = PenpotSync(api_key=api_key, base_url=penpot_url)
    file_id = input("Enter Penpot File ID: ").strip()

    if file_id:
        tokens = sync.extract_tokens(file_id=file_id)
        output_file = Path(__file__).parent.parent / "tokens.json"
        sync.save_tokens(tokens, output_file)
        print(f"✓ Tokens extracted and saved to: {output_file}")
        return output_file

    return None


def demo_transform_to_css(tokens_file: Path):
    """Transform tokens to CSS format."""
    print("\n" + "=" * 60)
    print("DEMO 2: Transform Tokens to CSS")
    print("=" * 60)

    if not tokens_file or not tokens_file.exists():
        print("⚠️  No tokens file found, skipping CSS transform")
        return

    sync = PenpotSync()

    with open(tokens_file) as f:
        tokens = json.load(f)

    # Transform to CSS
    css_output = sync.transform(tokens, format="css", options={"prefix": "ds"})

    output_file = tokens_file.parent / "tokens.css"
    with open(output_file, "w") as f:
        f.write(css_output)

    print(f"✓ CSS output saved to: {output_file}")
    print("\n📄 CSS Preview:")
    print("-" * 40)
    print(css_output[:500] + "..." if len(css_output) > 500 else css_output)


def demo_transform_to_ios(tokens_file: Path):
    """Transform tokens to iOS Swift format."""
    print("\n" + "=" * 60)
    print("DEMO 3: Transform Tokens to iOS Swift")
    print("=" * 60)

    if not tokens_file or not tokens_file.exists():
        print("⚠️  No tokens file found, skipping iOS transform")
        return

    sync = PenpotSync()

    with open(tokens_file) as f:
        tokens = json.load(f)

    # Transform to iOS Swift
    swift_output = sync.transform(
        tokens,
        format="ios",
        options={"prefix": "DS", "uiimport": True}
    )

    output_file = tokens_file.parent / "DesignTokens.swift"
    with open(output_file, "w") as f:
        f.write(swift_output)

    print(f"✓ iOS Swift output saved to: {output_file}")


def demo_transform_to_android(tokens_file: Path):
    """Transform tokens to Android XML format."""
    print("\n" + "=" * 60)
    print("DEMO 4: Transform Tokens to Android XML")
    print("=" * 60)

    if not tokens_file or not tokens_file.exists():
        print("⚠️  No tokens file found, skipping Android transform")
        return

    sync = PenpotSync()

    with open(tokens_file) as f:
        tokens = json.load(f)

    # Transform to Android XML
    android_output = sync.transform(tokens, format="android")

    output_dir = tokens_file.parent / "android"
    output_dir.mkdir(exist_ok=True)

    # Save colors.xml
    colors_file = output_dir / "colors.xml"
    colors_content = android_output.get("colors", "")
    with open(colors_file, "w") as f:
        f.write(colors_content)
    print(f"✓ Android colors.xml saved to: {colors_file}")

    # Save dimens.xml
    dimens_file = output_dir / "dimens.xml"
    dimens_content = android_output.get("dimens", "")
    with open(dimens_file, "w") as f:
        f.write(dimens_content)
    print(f"✓ Android dimens.xml saved to: {dimens_file}")


def demo_diff():
    """Demonstrate token diffing between versions."""
    print("\n" + "=" * 60)
    print("DEMO 5: Token Version Diff")
    print("=" * 60)

    tokens_file = Path(__file__).parent.parent / "tokens.json"

    if not tokens_file.exists():
        print("⚠️  No tokens file found, skipping diff demo")
        return

    # Create a mock "before" version by modifying some values
    with open(tokens_file) as f:
        current_tokens = json.load(f)

    before_tokens = json.loads(json.dumps(current_tokens))
    if "colors" in before_tokens and "primary" in before_tokens["colors"]:
        before_tokens["colors"]["primary"]["value"] = "#1d4ed8"  # Changed from #3b82f6

    # Save before version
    before_file = tokens_file.parent / "tokens-v1.json"
    with open(before_file, "w") as f:
        json.dump(before_tokens, f, indent=2)

    # Compare versions
    sync = PenpotSync()
    diff_result = sync.diff_tokens(before_tokens, current_tokens)

    print(f"✓ Diff computed between {before_file.name} and {tokens_file.name}")
    print(f"\n📊 Diff Summary:")
    print(f"  Added: {len(diff_result.get('added', []))} tokens")
    print(f"  Removed: {len(diff_result.get('removed', []))} tokens")
    print(f"  Changed: {len(diff_result.get('changed', []))} tokens")
    print(f"  Breaking: {len(diff_result.get('breaking', []))} changes")

    if diff_result.get("changed"):
        print("\n🔄 Changed Tokens:")
        for change in diff_result["changed"]:
            print(f"  - {change['path']}: {change['from']} → {change['to']}")


def main():
    """Run all demonstrations."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   penpot-design-system-sync - Basic Usage Examples          ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    print("\n📋 Demos to run:")
    print("  1. Extract tokens from Penpot (or use mock data)")
    print("  2. Transform to CSS")
    print("  3. Transform to iOS Swift")
    print("  4. Transform to Android XML")
    print("  5. Compare token versions")

    # Run demos
    tokens_file = demo_extract_tokens()

    demo_transform_to_css(tokens_file)
    demo_transform_to_ios(tokens_file)
    demo_transform_to_android(tokens_file)
    demo_diff()

    print("\n" + "=" * 60)
    print("✓ All demos completed!")
    print("=" * 60)

    print("\n📁 Output files created in examples/ directory:")
    output_dir = Path(__file__).parent.parent
    for f in output_dir.glob("tokens*"):
        print(f"  - {f.name}")
    for f in output_dir.glob("DesignTokens*"):
        print(f"  - {f.name}")
    for f in (output_dir / "android").glob("*.xml"):
        print(f"  - android/{f.name}")


if __name__ == "__main__":
    main()
