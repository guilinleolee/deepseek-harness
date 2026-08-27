#!/usr/bin/env python3
"""
brand_onboarding.py - 60-second brand onboarding: URL → semantic color/font tokens

Extracts color palette and typography from a brand URL to generate
design tokens compatible with diagram-design skill.

Usage:
    python brand_onboarding.py --url "https://brand.com"
    python brand_onboarding.py --url "https://brand.com" --output tokens.json
    python brand_onboarding.py --extract-colors image.png
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

try:
    import webcolors
except ImportError:
    print("Installing webcolors...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "webcolors", "-q"])
    import webcolors


def fetch_html(url: str) -> str:
    """Fetch HTML content from URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_colors_from_html(html: str) -> dict:
    """Extract color palette from HTML/CSS."""
    colors = {
        "primary": None,
        "secondary": None,
        "accent": None,
        "background": None,
        "text": None,
        "palette": []
    }

    # Extract CSS variables
    var_pattern = re.compile(r"(--[\w-]+):\s*([^;]+);")
    for match in var_pattern.finditer(html):
        var = match.group(1)
        value = match.group(2).strip()
        if value.startswith("#") or value.startswith("rgb"):
            if "primary" in var.lower():
                colors["primary"] = value
            elif "secondary" in var.lower():
                colors["secondary"] = value
            elif "accent" in var.lower():
                colors["accent"] = value
            elif "background" in var.lower() or "bg" in var.lower():
                colors["background"] = value
            elif "text" in var.lower() or "color" in var.lower():
                colors["text"] = value

    # Extract inline colors
    hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})\b', html)
    unique_colors = list(dict.fromkeys(f"#{c}" for c in hex_colors))

    # Filter out very light/dark colors
    meaningful_colors = [c for c in unique_colors if is_meaningful_color(c)]
    colors["palette"] = meaningful_colors[:10]  # Top 10

    # Try to identify primary/secondary from usage frequency
    if not colors["primary"] and meaningful_colors:
        colors["primary"] = find_most_used_color(meaningful_colors, html)

    return colors


def extract_fonts_from_html(html: str) -> dict:
    """Extract typography from HTML."""
    fonts = {
        "title": None,
        "body": None,
        "mono": None
    }

    # Google Fonts
    font_pattern = re.compile(r'fonts\.googleapis\.com/css\?[^"\']*family=([^"\'&]+)')
    for match in font_pattern.finditer(html):
        family = match.group(1).replace("+", " ")
        if not fonts["body"]:
            fonts["body"] = family
        elif not fonts["title"]:
            fonts["title"] = family

    # CSS font-family
    font_family_pattern = re.compile(r'font-family:\s*([^;]+);')
    for match in font_family_pattern.finditer(html):
        family = match.group(1).strip().strip("'\"").split(",")[0].strip()
        if "mono" in family.lower() or "code" in family.lower():
            fonts["mono"] = family
        elif not fonts["body"]:
            fonts["body"] = family

    return fonts


def extract_semantic_tokens(url: str) -> dict:
    """Extract complete semantic design tokens from URL."""
    print(f"Fetching {url}...")
    html = fetch_html(url)
    print("Analyzing colors and typography...")

    colors = extract_colors_from_html(html)
    fonts = extract_fonts_from_html(html)

    tokens = {
        "source_url": url,
        "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "color": {
            "--paper": colors.get("background") or "#ffffff",
            "--ink": colors.get("text") or "#1a1a2e",
            "--muted": "#6b7280",
            "--paper-2": "#f8fafc",
            "--accent": colors.get("accent") or colors.get("primary") or "#3b82f6",
            "--primary": colors.get("primary") or "#3b82f6",
            "--secondary": colors.get("secondary") or "#10b981",
        },
        "palette": colors["palette"],
        "font": {
            "--title": fonts.get("title") or "'Instrument Serif', Georgia, serif",
            "--node-name": fonts.get("body") or "'Inter', system-ui, sans-serif",
            "--sublabel": fonts.get("mono") or "'JetBrains Mono', 'Fira Code', monospace",
        },
        "typography": fonts,
    }

    return tokens


def generate_diagram_tokens(semantic_tokens: dict, variant: str = "minimal-light") -> dict:
    """Generate diagram-design compatible tokens."""
    tokens = {
        "source_url": semantic_tokens["source_url"],
        "variant": variant,
        "paper": semantic_tokens["color"]["--paper"],
        "ink": semantic_tokens["color"]["--ink"],
        "muted": semantic_tokens["color"]["--muted"],
        "paper_2": semantic_tokens["color"]["--paper-2"],
        "accent": semantic_tokens["color"]["--accent"],
        "title_font": semantic_tokens["font"]["--title"],
        "node_font": semantic_tokens["font"]["--node-name"],
        "sublabel_font": semantic_tokens["font"]["--sublabel"],
    }

    if variant == "minimal-dark":
        tokens.update({
            "paper": "#0f172a",
            "ink": "#f1f5f9",
            "muted": "#94a3b8",
            "paper_2": "#1e293b",
            "accent": "#60a5fa",
        })
    elif variant == "full-editorial":
        tokens.update({
            "paper": "#fefefe",
            "ink": "#18181b",
            "muted": "#71717a",
            "paper_2": "#f4f4f5",
            "accent": "#e11d48",
        })

    return tokens


def is_meaningful_color(hex_color: str) -> bool:
    """Check if color is meaningful (not too light or too dark)."""
    try:
        rgb = webcolors.hex_to_rgb(hex_color)
        r, g, b = rgb.red / 255, rgb.green / 255, rgb.blue / 255
        # Calculate luminance
        lum = 0.299 * r * r + 0.587 * g * g + 0.114 * b * b
        return 0.1 < lum < 0.9  # Not pure white or black
    except:
        return True


def find_most_used_color(colors: list, html: str) -> str:
    """Find the most frequently used color in HTML."""
    counts = {}
    for color in colors:
        count = html.count(color)
        if count > 0:
            counts[color] = count
    if counts:
        return max(counts, key=counts.get)
    return colors[0] if colors else "#3b82f6"


def extract_colors_from_image(image_path: str) -> list[str]:
    """Extract dominant colors from an image."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((100, 100))

        colors = {}
        for pixel in img.getdata():
            r, g, b = pixel
            hex_c = f"#{r:02x}{g:02x}{b:02x}"
            if is_meaningful_color(hex_c):
                colors[hex_c] = colors.get(hex_c, 0) + 1

        sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_colors[:10]]
    except Exception as e:
        print(f"Error extracting from image: {e}", file=sys.stderr)
        return []


def generate_css(tokens: dict) -> str:
    """Generate CSS from tokens."""
    css = f"""<style>
  :root {{
    --paper: {tokens.get('paper', '#ffffff')};
    --ink: {tokens.get('ink', '#1a1a2e')};
    --muted: {tokens.get('muted', '#6b7280')};
    --paper-2: {tokens.get('paper_2', '#f8fafc')};
    --accent: {tokens.get('accent', '#3b82f6')};
  }}
  text {{ font-family: {tokens.get('node_font', 'system-ui')}; }}
</style>"""
    return css


def main():
    parser = argparse.ArgumentParser(description="60-second brand onboarding: URL → design tokens")
    parser.add_argument("--url", "-u", help="Brand URL to analyze")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--css", help="Output CSS file")
    parser.add_argument("--extract-colors", "-e", help="Extract colors from image")
    parser.add_argument("--variant", "-v", choices=["minimal-light", "minimal-dark", "full-editorial"],
                        default="minimal-light", help="Color variant")
    args = parser.parse_args()

    if args.extract_colors:
        colors = extract_colors_from_image(args.extract_colors)
        print("Extracted colors:")
        for c in colors:
            print(f"  {c}")
        if args.output:
            with open(args.output, "w") as f:
                json.dump({"colors": colors}, f, indent=2)
        return

    if args.url:
        semantic_tokens = extract_semantic_tokens(args.url)
        diagram_tokens = generate_diagram_tokens(semantic_tokens, args.variant)

        print("\n" + "=" * 50)
        print("Brand Onboarding Complete!")
        print("=" * 50)

        print("\nColor Tokens:")
        for key, value in diagram_tokens.items():
            if key not in ("source_url", "variant", "title_font", "node_font", "sublabel_font"):
                print(f"  --{key}: {value}")

        print("\nFont Tokens:")
        for key, value in semantic_tokens["font"].items():
            print(f"  {key}: {value}")

        if args.output:
            Path(args.output).write_text(json.dumps(diagram_tokens, indent=2), encoding="utf-8")
            print(f"\nTokens saved to: {args.output}")

        if args.css:
            css = generate_css(diagram_tokens)
            Path(args.css).write_text(css, encoding="utf-8")
            print(f"CSS saved to: {args.css}")

        print("\nCSS snippet:")
        print(generate_css(diagram_tokens))
        return

    parser.print_help()
    print("\nExample:")
    print("  python brand_onboarding.py --url https://stripe.com --output stripe-tokens.json")


if __name__ == "__main__":
    main()
