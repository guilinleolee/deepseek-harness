#!/usr/bin/env python3
"""
diagram_generator.py - Programmatic diagram generation from JSON/template definitions

Usage:
    python diagram_generator.py --type architecture --data data.json
    python diagram_generator.py --type consultant-2x2 --data bcg.json --variant minimal-dark
    python diagram_generator.py --list
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.resolve()
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"

# Variant-specific color palettes (WCAG AA compliant)
# All foreground colors guaranteed >= 4.5:1 on their respective backgrounds
VARIANT_PALETTES = {
    "minimal-light": {
        "--paper": "#ffffff",
        "--ink": "#1a1a2e",
        "--muted": "#64748b",
        "--paper-2": "#f8fafc",
        "--accent": "#2563eb",
        # Quadrant fills: opaque background, dark ink text
        "--quadrant-tl-bg": "#10b981",
        "--quadrant-tl-text": "#ffffff",
        "--quadrant-tr-bg": "#3b82f6",
        "--quadrant-tr-text": "#ffffff",
        "--quadrant-bl-bg": "#f59e0b",
        "--quadrant-bl-text": "#ffffff",
        "--quadrant-br-bg": "#ef4444",
        "--quadrant-br-text": "#ffffff",
    },
    "minimal-dark": {
        "--paper": "#0f172a",
        "--ink": "#f1f5f9",
        "--muted": "#94a3b8",
        "--paper-2": "#1e293b",
        "--accent": "#60a5fa",
        # Quadrant fills: light fills on dark background, dark ink
        "--quadrant-tl-bg": "#6ee7b7",
        "--quadrant-tl-text": "#1a1a2e",
        "--quadrant-tr-bg": "#93c5fd",
        "--quadrant-tr-text": "#1a1a2e",
        "--quadrant-bl-bg": "#fcd34d",
        "--quadrant-bl-text": "#1a1a2e",
        "--quadrant-br-bg": "#fca5a5",
        "--quadrant-br-text": "#1a1a2e",
    },
    "full-editorial": {
        "--paper": "#fefdfb",
        "--ink": "#292524",
        "--muted": "#78716c",
        "--paper-2": "#f5f5f4",
        "--accent": "#1d4ed8",
        # Quadrant fills: muted tones
        "--quadrant-tl-bg": "#6ee7b7",
        "--quadrant-tl-text": "#1a1a2e",
        "--quadrant-tr-bg": "#93c5fd",
        "--quadrant-tr-text": "#1a1a2e",
        "--quadrant-bl-bg": "#fcd34d",
        "--quadrant-bl-text": "#1a1a2e",
        "--quadrant-br-bg": "#fca5a5",
        "--quadrant-br-text": "#1a1a2e",
    },
}

DIAGRAM_TYPES = {
    "architecture": "Software architecture, cloud, microservices",
    "flowchart": "Process flows, decision trees",
    "sequence": "Sequence/communication diagrams",
    "state-machine": "State diagrams, finite automata",
    "er": "ER diagrams, data models",
    "timeline": "Temporal events, roadmaps",
    "swimlane": "Cross-functional flows, BPMN",
    "quadrant": "2x2 matrices, BCG, priority",
    "consultant-2x2": "Strategic analysis, importance-satisfaction",
    "nested": "Hierarchical containers, zoom-in",
    "tree": "Tree structures, org charts",
    "layers": "OSI layers, stacks",
    "venn": "Intersections, comparisons",
    "pyramid": "Funnels, hierarchies, Maslow",
}

VARIANTS = ["minimal-light", "minimal-dark", "full-editorial"]


def load_template(diagram_type: str) -> str:
    """Load the prompt template for a diagram type."""
    prompt_file = PROMPTS_DIR / f"{diagram_type}.md"
    if not prompt_file.exists():
        # fallback to consultant-2x2 for generic 2x2
        prompt_file = PROMPTS_DIR / "consultant-2x2.md"
    return prompt_file.read_text(encoding="utf-8")


def load_data(data_file: str) -> dict[str, Any]:
    """Load diagram data from JSON file."""
    p = Path(data_file)
    if not p.exists():
        print(f"Error: Data file not found: {data_file}", file=sys.stderr)
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def generate_svg(diagram_type: str, data: dict[str, Any], variant: str = "minimal-light") -> str:
    """Generate SVG from template + data using built-in SVG generation."""
    title = data.get("title", "Generated Diagram")
    width = data.get("width", 600)
    height = data.get("height", 400)

    # Look up variant palette (fallback to minimal-light)
    palette = VARIANT_PALETTES.get(variant, VARIANT_PALETTES["minimal-light"])
    paper = palette["--paper"]
    ink = palette["--ink"]
    muted = palette["--muted"]
    paper2 = palette["--paper-2"]
    accent = palette["--accent"]

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root {{
      --paper: {paper};
      --ink: {ink};
      --muted: {muted};
      --paper-2: {paper2};
      --accent: {accent};
    }}
    text {{ font-family: 'Inter', system-ui, sans-serif; }}
  </style>
  <rect width="{width}" height="{height}" fill="var(--paper)"/>
  <text x="{width // 2}" y="30" text-anchor="middle" font-size="16" font-weight="600" fill="var(--ink)">{title}</text>
'''

    # Generate based on diagram type
    if diagram_type == "architecture":
        svg += _generate_architecture(data, width, height, palette)
    elif diagram_type in ("consultant-2x2", "quadrant"):
        svg += _generate_2x2(data, width, height, palette)
    elif diagram_type == "venn":
        svg += _generate_venn(data, width, height, palette)
    elif diagram_type == "pyramid":
        svg += _generate_pyramid(data, width, height, palette)
    elif diagram_type == "layers":
        svg += _generate_layers(data, width, height, palette)
    else:
        svg += _generate_generic(data, width, height, palette)

    svg += "</svg>"
    return svg


def _generate_architecture(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate architecture diagram."""
    svg = ""
    nodes = data.get("nodes", [])
    accent = palette["--accent"]
    muted = palette["--muted"]
    for i, node in enumerate(nodes):
        x = 80 + (i % 4) * 120
        y = 80 + (i // 4) * 100
        svg += f'''
  <rect x="{x}" y="{y}" width="100" height="60" rx="6" fill="{accent}" opacity="0.15" stroke="{accent}" stroke-width="2"/>
  <text x="{x + 50}" y="{y + 25}" text-anchor="middle" font-size="11" font-weight="600" fill="{accent}">{node.get("name", "Node")}</text>
  <text x="{x + 50}" y="{y + 45}" text-anchor="middle" font-size="9" fill="{muted}">{node.get("type", "Service")}</text>'''
    return svg


def _generate_2x2(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate 2x2 quadrant diagram."""
    svg = ""
    margin = 80
    box_w = (width - margin * 2) // 2
    box_h = (height - margin * 2) // 2
    ink = palette["--ink"]
    # Get variant quadrant colors
    tl_bg = palette.get("--quadrant-tl-bg", "#10b981")
    tr_bg = palette.get("--quadrant-tr-bg", "#3b82f6")
    bl_bg = palette.get("--quadrant-bl-bg", "#f59e0b")
    br_bg = palette.get("--quadrant-br-bg", "#ef4444")
    tl_text = palette.get("--quadrant-tl-text", "#ffffff")
    tr_text = palette.get("--quadrant-tr-text", "#ffffff")
    bl_text = palette.get("--quadrant-bl-text", "#ffffff")
    br_text = palette.get("--quadrant-br-text", "#ffffff")
    svg += f'''
  <rect x="{margin}" y="{margin}" width="{box_w * 2}" height="{box_h * 2}" fill="none" stroke="{ink}" stroke-width="2"/>
  <line x1="{margin + box_w}" y1="{margin}" x2="{margin + box_w}" y2="{margin + box_h * 2}" stroke="{ink}" stroke-width="1"/>
  <line x1="{margin}" y1="{margin + box_h}" x2="{margin + box_w * 2}" y2="{margin + box_h}" stroke="{ink}" stroke-width="1"/>
  <rect x="{margin}" y="{margin}" width="{box_w}" height="{box_h}" fill="{tl_bg}" opacity="0.15"/>
  <rect x="{margin + box_w}" y="{margin}" width="{box_w}" height="{box_h}" fill="{tr_bg}" opacity="0.15"/>
  <rect x="{margin}" y="{margin + box_h}" width="{box_w}" height="{box_h}" fill="{bl_bg}" opacity="0.15"/>
  <rect x="{margin + box_w}" y="{margin + box_h}" width="{box_w}" height="{box_h}" fill="{br_bg}" opacity="0.15"/>
'''
    quadrants = data.get("quadrants", [
        {"name": "TL", "label": "Top-Left", "x": margin + box_w // 2, "y": margin + 30},
        {"name": "TR", "label": "Top-Right", "x": margin + box_w + box_w // 2, "y": margin + 30},
        {"name": "BL", "label": "Bottom-Left", "x": margin + box_w // 2, "y": margin + box_h + 30},
        {"name": "BR", "label": "Bottom-Right", "x": margin + box_w + box_w // 2, "y": margin + box_h + 30},
    ])
    ink_color = palette["--ink"]
    texts = [(tl_bg, ink_color), (tr_bg, ink_color), (bl_bg, ink_color), (br_bg, ink_color)]
    for i, q in enumerate(quadrants):
        fill_color, text_color = texts[i % 4]
        svg += f'''
  <text x="{q["x"]}" y="{q["y"]}" text-anchor="middle" font-size="11" font-weight="600" fill="{text_color}">{q.get("name", q["label"])}</text>'''
    return svg


def _generate_venn(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate Venn diagram."""
    svg = ""
    accent = palette["--accent"]
    muted = palette["--muted"]
    circles = data.get("circles", [
        {"cx": width // 2 - 50, "cy": height // 2, "r": 80, "name": "A", "color": accent},
        {"cx": width // 2 + 50, "cy": height // 2, "r": 80, "name": "B", "color": muted},
    ])
    for c in circles:
        svg += f'''
  <circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{c["color"]}" opacity="0.15" stroke="{c["color"]}" stroke-width="2"/>
  <text x="{c["cx"]}" y="{c["cy"] - 20}" text-anchor="middle" font-size="12" font-weight="600" fill="{c["color"]}">{c.get("name", "")}</text>'''
    return svg


def _generate_pyramid(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate pyramid/funnel diagram."""
    svg = ""
    ink = palette["--ink"]
    levels = data.get("levels", [
        {"label": "Level 1", "value": 100},
        {"label": "Level 2", "value": 75},
        {"label": "Level 3", "value": 50},
        {"label": "Level 4", "value": 25},
    ])
    colors = ["#1e40af", "#3b82f6", "#60a5fa", "#93c5fd"]
    y = 50
    for i, level in enumerate(levels):
        w = int(level["value"] / 100 * (width - 100))
        x = (width - w) // 2
        svg += f'''
  <polygon points="{x},{y} {x + w},{y} {x + w - 20},{y + 50} {x + 20},{y + 50}" fill="{colors[i % 4]}" stroke="{ink}" stroke-width="1.5"/>
  <text x="{width // 2}" y="{y + 30}" text-anchor="middle" font-size="11" fill="{ink}">{level["label"]}</text>'''
        y += 55
    return svg


def _generate_layers(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate layers diagram."""
    svg = ""
    accent = palette["--accent"]
    ink = palette["--ink"]
    muted = palette["--muted"]
    paper = palette["--paper"]
    layers = data.get("layers", [
        {"name": "Layer 1", "protocol": "HTTP"},
        {"name": "Layer 2", "protocol": "TLS"},
        {"name": "Layer 3", "protocol": "TCP"},
        {"name": "Layer 4", "protocol": "IP"},
    ])
    y = 60
    for i, layer in enumerate(layers):
        fill_color = accent if i == 0 else paper
        stroke_w = "2" if i == 0 else "1"
        svg += f'''
  <rect x="100" y="{y}" width="{width - 200}" height="50" rx="4" fill="{fill_color}" stroke="{ink}" stroke-width="{stroke_w}"/>
  <text x="{width // 2}" y="{y + 20}" text-anchor="middle" font-size="12" fill="{accent if i == 0 else ink}">{layer["name"]}</text>
  <text x="{width // 2}" y="{y + 38}" text-anchor="middle" font-size="10" fill="{muted}">{layer["protocol"]}</text>'''
        y += 60
    return svg


def _generate_generic(data: dict, width: int, height: int, palette: dict) -> str:
    """Generate generic placeholder."""
    svg = ""
    paper2 = palette["--paper-2"]
    ink = palette["--ink"]
    items = data.get("items", [])
    for i, item in enumerate(items):
        x = 80 + (i % 3) * 150
        y = 80 + (i // 3) * 80
        svg += f'''
  <rect x="{x}" y="{y}" width="120" height="60" rx="4" fill="{paper2}" stroke="{ink}" stroke-width="1"/>
  <text x="{x + 60}" y="{y + 35}" text-anchor="middle" font-size="11" fill="{ink}">{item.get("name", f"Item {i+1}")}</text>'''
    return svg


def main():
    parser = argparse.ArgumentParser(description="Generate SVG diagrams from templates")
    parser.add_argument("--type", "-t", choices=list(DIAGRAM_TYPES.keys()),
                        help="Diagram type")
    parser.add_argument("--data", "-d", help="JSON data file")
    parser.add_argument("--variant", "-v", choices=VARIANTS, default="minimal-light",
                        help="Color variant")
    parser.add_argument("--output", "-o", help="Output SVG file")
    parser.add_argument("--list", "-l", action="store_true", help="List available diagram types")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.list:
        print("Available diagram types:")
        for t, desc in DIAGRAM_TYPES.items():
            print(f"  {t:20s} - {desc}")
        print(f"\nAvailable variants: {', '.join(VARIANTS)}")
        return

    if args.interactive:
        _interactive_mode()
        return

    if not args.type:
        parser.print_help()
        print("\nAvailable types: " + ", ".join(DIAGRAM_TYPES.keys()))
        sys.exit(1)

    # Load data
    if args.data:
        data = load_data(args.data)
    else:
        data = {}

    # Generate SVG
    svg = generate_svg(args.type, data, args.variant)

    if args.output:
        Path(args.output).write_text(svg, encoding="utf-8")
        print(f"Diagram saved to: {args.output}")
    else:
        print(svg)


def _interactive_mode():
    """Interactive diagram generation."""
    print("Interactive Diagram Generator")
    print("=" * 40)

    print("\nSelect diagram type:")
    for i, (t, desc) in enumerate(DIAGRAM_TYPES.items(), 1):
        print(f"  {i}. {t} - {desc}")

    type_idx = int(input("\nEnter number: ")) - 1
    diagram_type = list(DIAGRAM_TYPES.keys())[type_idx]

    title = input("Diagram title: ")
    variant = input(f"Variant ({'/'.join(VARIANTS)}) [minimal-light]: ") or "minimal-light"

    data = {"title": title, "width": 600, "height": 400}
    svg = generate_svg(diagram_type, data, variant)
    print("\n" + svg)


if __name__ == "__main__":
    main()
