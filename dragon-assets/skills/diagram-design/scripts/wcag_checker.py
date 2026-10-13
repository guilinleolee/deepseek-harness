#!/usr/bin/env python3
"""
wcag_checker.py - WCAG AA contrast ratio checking for SVG colors

Usage:
    python wcag_checker.py --svg diagram.svg
    python wcag_checker.py --color "#3b82f6" "#ffffff"
    python wcag_checker.py --tokens tokens.json
    python wcag_checker.py --auto-check  # Check all CSS variables
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Optional


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color[0] * 2 + hex_color[1] * 2 + hex_color[2] * 2
    if len(hex_color) != 6:
        return (0, 0, 0)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex."""
    return f"#{r:02x}{g:02x}{b:02x}"


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    def channel(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    l1 = relative_luminance(*rgb1)
    l2 = relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_wcag_aa(ratio: float, is_large_text: bool = False) -> dict:
    """Check if contrast ratio meets WCAG AA requirements."""
    if is_large_text:
        return {
            "pass": ratio >= 3.0,
            "required": 3.0,
            "level": "AA Large" if ratio >= 3.0 else "Fail",
            "suggestion": "Use a darker/lighter variant of this color" if ratio < 3.0 else None
        }
    return {
        "pass": ratio >= 4.5,
        "required": 4.5,
        "level": "AA Normal" if ratio >= 4.5 else ("AA Large" if ratio >= 3.0 else "Fail"),
        "suggestion": "Use a darker/lighter variant of this color" if ratio < 4.5 else None
    }


def check_wcag_aaa(ratio: float, is_large_text: bool = False) -> dict:
    """Check if contrast ratio meets WCAG AAA requirements."""
    if is_large_text:
        return {
            "pass": ratio >= 4.5,
            "required": 4.5,
            "level": "AAA" if ratio >= 4.5 else "AA" if ratio >= 3.0 else "Fail"
        }
    return {
        "pass": ratio >= 7.0,
        "required": 7.0,
        "level": "AAA" if ratio >= 7.0 else ("AA" if ratio >= 4.5 else ("AA Large" if ratio >= 3.0 else "Fail"))
    }


def _resolve_css_var(color: str, css_vars: dict[str, str]) -> str:
    """Resolve a CSS variable reference (e.g. 'var(--paper)') to its actual value."""
    if color.startswith("var(") and color.endswith(")"):
        var_name = color[4:-1].strip()
        css_key = var_name.lstrip("-")
        if css_key in css_vars:
            return css_vars[css_key]
    return color


def extract_colors_from_svg(svg_path: str) -> dict[str, list[str]]:
    """Extract colors from SVG file."""
    content = Path(svg_path).read_text(encoding="utf-8")

    colors = {
        "fill": [],
        "stroke": [],
        "css_vars": {},
        "text": []
    }

    # Extract CSS variables
    var_pattern = re.compile(r"--([a-z-]+):\s*([^;]+);")
    for match in var_pattern.finditer(content):
        var_name = match.group(1)
        value = match.group(2).strip()
        if value.startswith("#") or value.startswith("rgb"):
            colors["css_vars"][var_name] = value

    # Extract fill colors (resolve CSS variables before adding)
    fill_pattern = re.compile(r'fill="([^"#][^"]*)"')
    for match in fill_pattern.finditer(content):
        raw = match.group(1)
        resolved = _resolve_css_var(raw, colors["css_vars"])
        if resolved not in colors["fill"]:
            colors["fill"].append(resolved)

    # Extract stroke colors
    stroke_pattern = re.compile(r'stroke="([^"#][^"]*)"')
    for match in stroke_pattern.finditer(content):
        if match.group(1) not in colors["stroke"]:
            colors["stroke"].append(match.group(1))

    # Extract fill with hex
    hex_fill = re.compile(r'fill="(#[0-9a-fA-F]{3,6})"')
    for match in hex_fill.finditer(content):
        if match.group(1) not in colors["fill"]:
            colors["fill"].append(match.group(1))

    # Extract text elements
    text_pattern = re.compile(r'<text[^>]*fill="(#[0-9a-fA-F]{3,6})"')
    for match in text_pattern.finditer(content):
        if match.group(1) not in colors["text"]:
            colors["text"].append(match.group(1))

    return colors


def suggest_better_color(bad_color: str, bg_color: str, direction: str = "auto") -> str:
    """Suggest a better color for contrast."""
    rgb = hex_to_rgb(bad_color)
    bg_rgb = hex_to_rgb(bg_color)

    # Calculate direction to move
    if direction == "auto":
        bg_lum = relative_luminance(*bg_rgb)
        direction = "lighter" if bg_lum > 0.5 else "darker"

    factor = 0.1 if direction == "lighter" else -0.1
    new_r = max(0, min(255, int(rgb[0] + (255 - rgb[0]) * factor if direction == "lighter" else rgb[0] * (1 + factor))))
    new_g = max(0, min(255, int(rgb[1] + (255 - rgb[1]) * factor if direction == "lighter" else rgb[1] * (1 + factor))))
    new_b = max(0, min(255, int(rgb[2] + (255 - rgb[2]) * factor if direction == "lighter" else rgb[2] * (1 + factor))))

    return rgb_to_hex(new_r, new_g, new_b)


def auto_check_svg(svg_path: str) -> list[dict]:
    """Automatically check all text/background pairs in SVG."""
    colors = extract_colors_from_svg(svg_path)
    results = []

    # Check CSS variable pairs
    bg_color = colors["css_vars"].get("paper", "#ffffff")
    ink_color = colors["css_vars"].get("ink", "#1a1a2e")
    accent_color = colors["css_vars"].get("accent", "#3b82f6")

    pairs = [
        ("ink", ink_color, "paper", bg_color, "Normal text on background"),
        ("accent", accent_color, "paper", bg_color, "Accent on background"),
    ]

    for name1, c1, name2, c2, desc in pairs:
        ratio = contrast_ratio(c1, c2)
        aa_check = check_wcag_aa(ratio, is_large_text=False)
        results.append({
            "pair": f"{name1}/{name2}",
            "colors": f"{c1} / {c2}",
            "description": desc,
            "ratio": round(ratio, 2),
            **aa_check
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="WCAG AA contrast checker for SVG diagrams")
    parser.add_argument("--svg", "-s", help="SVG file to check")
    parser.add_argument("--color", "-c", nargs=2, help="Two colors to compare: \"#color1\" \"#color2\"")
    parser.add_argument("--tokens", "-t", help="JSON file with design tokens")
    parser.add_argument("--auto-check", "-a", action="store_true", help="Auto-check all CSS variables in SVG")
    parser.add_argument("--suggest", action="store_true", help="Suggest better colors")
    args = parser.parse_args()

    if args.color:
        c1, c2 = args.color
        ratio = contrast_ratio(c1, c2)
        aa = check_wcag_aa(ratio)
        aaa = check_wcag_aaa(ratio)
        print(f"Contrast ratio: {ratio:.2f}:1")
        print(f"WCAG AA (normal):  {'PASS' if aa['pass'] else 'FAIL'} (requires 4.5:1)")
        print(f"WCAG AA (large):  {'PASS' if ratio >= 3.0 else 'FAIL'} (requires 3.0:1)")
        print(f"WCAG AAA (normal): {'PASS' if aaa['pass'] else 'FAIL'} (requires 7.0:1)")
        return

    if args.tokens:
        tokens = json.loads(Path(args.tokens).read_text())
        bg = tokens.get("--paper", "#ffffff")
        for key, color in tokens.items():
            if key.startswith("--") and color.startswith("#"):
                ratio = contrast_ratio(color, bg)
                aa = check_wcag_aa(ratio)
                status = "[PASS]" if aa["pass"] else "[FAIL]"
                print(f"{status} {key}: {color} on {bg} = {ratio:.2f}:1 ({aa['level']})")
        return

    if args.auto_check and args.svg:
        results = auto_check_svg(args.svg)
        print(f"WCAG Contrast Check: {args.svg}")
        print("=" * 60)
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['pair']}: {r['ratio']}:1 ({r['level']})")
            print(f"   {r['colors']}")
            if r.get("suggestion"):
                print(f"   Suggestion: {r['suggestion']}")
        return

    if args.svg:
        colors = extract_colors_from_svg(args.svg)
        print(f"Colors found in {args.svg}:")
        print(f"  CSS Variables: {json.dumps(colors['css_vars'], indent=2)}")
        print(f"  Fills: {colors['fill']}")
        print(f"  Strokes: {colors['stroke']}")
        print(f"  Text: {colors['text']}")
        print("\nUse --auto-check to run full contrast analysis")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
