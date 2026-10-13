#!/usr/bin/env python3
"""
Penpot Design System Sync - Token Transformation Module
Transforms design tokens to various platform formats.
"""

import json
import re
from typing import Any, Dict, List


class TokenTransformer:
    """Transform design tokens to various output formats."""

    def __init__(self, tokens: Dict[str, Any]):
        self.tokens = tokens

    def transform(self, format: str, options: Dict[str, Any] = None) -> str:
        """Transform tokens to specified format."""
        options = options or {}

        if format == "json":
            return self.to_json(options)
        elif format == "css":
            return self.to_css(options)
        elif format == "scss":
            return self.to_scss(options)
        elif format == "ios":
            return self.to_ios(options)
        elif format == "android":
            return self.to_android(options)
        elif format == "yaml":
            return self.to_yaml(options)
        elif format == "tailwind":
            return self.to_tailwind(options)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_json(self, options: Dict[str, Any]) -> str:
        """Export tokens as JSON."""
        output = {"tokens": self.tokens}

        if options.get("includeSemantic"):
            output["semanticTokens"] = self.generate_semantic_tokens(options.get("prefix", ""))

        if options.get("includeW3C"):
            output["w3cTokens"] = self.generate_w3c_tokens()

        return json.dumps(output, indent=2, ensure_ascii=False)

    def to_css(self, options: Dict[str, Any]) -> str:
        """Export tokens as CSS custom properties."""
        prefix = options.get("prefix", "")
        lines = [":root {"]

        # Colors
        for color in self.tokens.get("colors", []):
            var_name = self.to_css_var_name(color["name"], prefix)
            opacity = color.get("opacity")
            value = color["value"]
            if opacity and opacity != 1:
                lines.append(f"  --color-{var_name}: {value} / {opacity};")
            else:
                lines.append(f"  --color-{var_name}: {value};")

        # Typography
        for typo in self.tokens.get("typography", []):
            var_name = self.to_css_var_name(typo["name"], prefix)
            lines.append(f"  --font-{var_name}-family: {typo['fontFamily']};")
            lines.append(f"  --font-{var_name}-size: {typo['fontSize']};")
            lines.append(f"  --font-{var_name}-weight: {typo['fontWeight']};")
            lines.append(f"  --font-{var_name}-line-height: {typo['lineHeight']};")

        # Spacing
        for space in self.tokens.get("spacing", []):
            var_name = self.to_css_var_name(space["name"], prefix)
            lines.append(f"  --{var_name}: {space['value']};")

        # Shadows
        for shadow in self.tokens.get("shadows", []):
            var_name = self.to_css_var_name(shadow["name"], prefix)
            lines.append(f"  --shadow-{var_name}: {shadow['value']};")

        # Borders
        for border in self.tokens.get("borders", []):
            var_name = self.to_css_var_name(border["name"], prefix)
            lines.append(f"  --border-{var_name}: {border['width']} solid {border['color']};")

        # Radii
        for radius in self.tokens.get("radii", []):
            var_name = self.to_css_var_name(radius["name"], prefix)
            lines.append(f"  --radius-{var_name}: {radius['value']};")

        lines.append("}")
        return "\n".join(lines)

    def to_scss(self, options: Dict[str, Any]) -> str:
        """Export tokens as SCSS variables."""
        prefix = options.get("prefix", "")
        lines = []

        # Colors
        lines.append("// Colors")
        for color in self.tokens.get("colors", []):
            var_name = self.to_css_var_name(color["name"], prefix)
            opacity = color.get("opacity")
            if opacity and opacity != 1:
                lines.append(f"$color-{var_name}: {color['value']}, {opacity};")
            else:
                lines.append(f"$color-{var_name}: {color['value']};")

        # Typography
        lines.append("\n// Typography")
        for typo in self.tokens.get("typography", []):
            var_name = self.to_css_var_name(typo["name"], prefix)
            lines.append(f"$font-{var_name}-family: {typo['fontFamily']};")
            lines.append(f"$font-{var_name}-size: {typo['fontSize']};")
            lines.append(f"$font-{var_name}-weight: {typo['fontWeight']};")
            lines.append(f"$font-{var_name}-line-height: {typo['lineHeight']};")

        # Spacing
        lines.append("\n// Spacing")
        for space in self.tokens.get("spacing", []):
            var_name = self.to_css_var_name(space["name"], prefix)
            lines.append(f"${var_name}: {space['value']};")

        # Shadows
        lines.append("\n// Shadows")
        for shadow in self.tokens.get("shadows", []):
            var_name = self.to_css_var_name(shadow["name"], prefix)
            lines.append(f"$shadow-{var_name}: {shadow['value']};")

        # Borders
        lines.append("\n// Borders")
        for border in self.tokens.get("borders", []):
            var_name = self.to_css_var_name(border["name"], prefix)
            lines.append(f"$border-{var_name}-width: {border['width']};")
            lines.append(f"$border-{var_name}-color: {border['color']};")

        # Radii
        lines.append("\n// Border Radius")
        for radius in self.tokens.get("radii", []):
            var_name = self.to_css_var_name(radius["name"], prefix)
            lines.append(f"$radius-{var_name}: {radius['value']};")

        return "\n".join(lines)

    def to_ios(self, options: Dict[str, Any]) -> str:
        """Export tokens as iOS Swift code."""
        prefix = options.get("prefix", "DS")
        lines = [
            "import UIKit",
            "",
            f"enum {prefix}Tokens {{",
            "    // MARK: - Colors"
        ]

        for color in self.tokens.get("colors", []):
            var_name = self.to_camel_case(color["name"])
            opacity = color.get("opacity", 1.0)
            if opacity != 1.0:
                lines.append(
                    f'    static let {var_name} = UIColor(red: {self.hex_to_rgb(color["value"])}, alpha: {opacity})'
                )
            else:
                lines.append(f'    static let {var_name} = UIColor(hex: "{color["value"]}") ?? .clear')

        lines.append("\n    // MARK: - Typography")
        for typo in self.tokens.get("typography", []):
            var_name = self.to_camel_case(typo["name"])
            lines.append(f'    static let {var_name}Font = UIFont(name: "{typo["fontFamily"]}", size: {self.px_to_float(typo["fontSize"])}) ?? .systemFont(ofSize: {self.px_to_float(typo["fontSize"])})')

        lines.append("\n    // MARK: - Spacing")
        for space in self.tokens.get("spacing", []):
            var_name = self.to_camel_case(space["name"].replace("spacing-", ""))
            lines.append(f'    static let {var_name}: CGFloat = {self.px_to_float(space["value"])}')

        lines.append("\n    // MARK: - Shadows")
        for shadow in self.tokens.get("shadows", []):
            var_name = self.to_camel_case(shadow["name"].replace("shadow-", ""))
            lines.append(f'    static let {var_name}Shadow = "{shadow["value"]}"')

        lines.append("}")
        return "\n".join(lines)

    def to_android(self, options: Dict[str, Any]) -> str:
        """Export tokens as Android XML resources."""
        lines = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<resources>"]

        # Colors
        lines.append("\n    <!-- Colors -->")
        for color in self.tokens.get("colors", []):
            var_name = self.to_android_name(color["name"])
            hex_value = color["value"].lstrip("#")
            lines.append(f'    <color name="color_{var_name}">#{hex_value}</color>')

        # Dimensions
        lines.append("\n    <!-- Spacing -->")
        for space in self.tokens.get("spacing", []):
            var_name = self.to_android_name(space["name"].replace("spacing-", "spacing_"))
            px_value = self.px_to_int(space["value"])
            lines.append(f'    <dimen name="{var_name}">{px_value}dp</dimen>')

        # Typography
        lines.append("\n    <!-- Typography -->")
        for typo in self.tokens.get("typography", []):
            var_name = self.to_android_name(typo["name"])
            lines.append(f'    <dimen name="font_{var_name}_size">{self.px_to_int(typo["fontSize"])}sp</dimen>')

        # Radii
        lines.append("\n    <!-- Border Radius -->")
        for radius in self.tokens.get("radii", []):
            var_name = self.to_android_name(radius["name"].replace("radius-", "radius_"))
            px_value = self.px_to_int(radius["value"])
            lines.append(f'    <dimen name="{var_name}">{px_value}dp</dimen>')

        lines.append("</resources>")
        return "\n".join(lines)

    def to_yaml(self, options: Dict[str, Any]) -> str:
        """Export tokens as YAML."""
        lines = ["tokens:"]

        if self.tokens.get("colors"):
            lines.append("  colors:")
            for color in self.tokens["colors"]:
                lines.append(f'    - name: "{color["name"]}"')
                lines.append(f'      value: "{color["value"]}"')
                if color.get("opacity"):
                    lines.append(f'      opacity: {color["opacity"]}')
                if color.get("category"):
                    lines.append(f'      category: "{color["category"]}"')

        if self.tokens.get("typography"):
            lines.append("  typography:")
            for typo in self.tokens["typography"]:
                lines.append(f'    - name: "{typo["name"]}"')
                lines.append(f'      fontFamily: "{typo["fontFamily"]}"')
                lines.append(f'      fontSize: "{typo["fontSize"]}"')
                lines.append(f'      fontWeight: "{typo["fontWeight"]}"')
                lines.append(f'      lineHeight: "{typo["lineHeight"]}"')

        if self.tokens.get("spacing"):
            lines.append("  spacing:")
            for space in self.tokens["spacing"]:
                lines.append(f'    - name: "{space["name"]}"')
                lines.append(f'      value: "{space["value"]}"')

        return "\n".join(lines)

    def to_tailwind(self, options: Dict[str, Any]) -> str:
        """Export tokens as Tailwind CSS config."""
        prefix = options.get("prefix", "")
        config = {"theme": {"extend": {}}}

        # Colors
        colors = {}
        for color in self.tokens.get("colors", []):
            var_name = color["name"].replace(f"{prefix}-" if prefix else "", "")
            colors[var_name] = color["value"]
        if colors:
            config["theme"]["extend"]["colors"] = colors

        # Font family
        fonts = {}
        for typo in self.tokens.get("typography", []):
            var_name = typo["name"].replace(f"{prefix}-" if prefix else "", "")
            fonts[var_name] = typo["fontFamily"]
        if fonts:
            config["theme"]["extend"]["fontFamily"] = fonts

        # Spacing
        spacing = {}
        for space in self.tokens.get("spacing", []):
            var_name = space["name"].replace("spacing-", "").replace(f"{prefix}-" if prefix else "", "")
            spacing[var_name] = space["value"]
        if spacing:
            config["theme"]["extend"]["spacing"] = spacing

        # Border radius
        radii = {}
        for radius in self.tokens.get("radii", []):
            var_name = radius["name"].replace("radius-", "").replace(f"{prefix}-" if prefix else "", "")
            radii[var_name] = radius["value"]
        if radii:
            config["theme"]["extend"]["borderRadius"] = radii

        return f"module.exports = {json.dumps(config, indent=2)}"

    def generate_semantic_tokens(self, prefix: str) -> Dict[str, str]:
        """Generate semantic token mappings."""
        semantic = {}

        for color in self.tokens.get("colors", []):
            if color.get("category") == "primary":
                var_name = self.to_css_var_name(color["name"], prefix)
                semantic["primary"] = f"var(--color-{var_name})"
            elif color.get("category") == "secondary":
                var_name = self.to_css_var_name(color["name"], prefix)
                semantic["secondary"] = f"var(--color-{var_name})"

        return semantic

    def generate_w3c_tokens(self) -> Dict[str, Any]:
        """Generate W3C Design Token format."""
        w3c = {"color": {}, "typography": {}, "spacing": {}, "shadow": {}}

        for color in self.tokens.get("colors", []):
            w3c["color"][color["name"]] = {
                "$type": "color",
                "$value": color["value"]
            }

        for typo in self.tokens.get("typography", []):
            w3c["typography"][typo["name"]] = {
                "$type": "typography",
                "$value": {
                    "fontFamily": {"$value": typo["fontFamily"]},
                    "fontSize": {"$value": typo["fontSize"]},
                    "fontWeight": {"$value": typo["fontWeight"]},
                    "lineHeight": {"$value": typo["lineHeight"]}
                }
            }

        for space in self.tokens.get("spacing", []):
            w3c["spacing"][space["name"]] = {
                "$type": "dimension",
                "$value": space["value"]
            }

        for shadow in self.tokens.get("shadows", []):
            w3c["shadow"][shadow["name"]] = {
                "$type": "shadow",
                "$value": shadow["value"]
            }

        return w3c

    # Helper methods
    def to_css_var_name(self, name: str, prefix: str) -> str:
        """Convert name to CSS variable name."""
        name = name.lower().replace(" ", "-").replace("_", "-")
        if prefix:
            return f"{prefix}-{name}"
        return name

    def to_camel_case(self, name: str) -> str:
        """Convert name to camelCase."""
        parts = name.lower().replace("-", " ").replace("_", " ").split()
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def to_android_name(self, name: str) -> str:
        """Convert name to Android resource name."""
        name = name.lower().replace("-", "_").replace(" ", "_")
        return re.sub(r"[^a-z0-9_]", "", name)

    def hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB tuple string."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"{r/255:.3f}, {g/255:.3f}, {b/255:.3f}"
        return "0, 0, 0"

    def px_to_float(self, value: str) -> float:
        """Convert px string to float."""
        return float(value.rstrip("px").rstrip("pt"))

    def px_to_int(self, value: str) -> int:
        """Convert px string to int."""
        return int(value.rstrip("px").rstrip("pt"))
