#!/usr/bin/env python3
"""
Penpot Design System Sync - Token Extraction Module
Extracts design tokens from Penpot files via API.
"""

import json
import re
import httpx
from typing import Any, Dict, List, Optional


class TokenExtractor:
    """Extract design tokens from Penpot."""

    def __init__(self, api_key: Optional[str] = None, api_endpoint: str = "https://api.penpot.app/v1"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.client = httpx.Client(timeout=30.0)

    def extract_tokens(self, file_id: str) -> Dict[str, Any]:
        """Extract all design tokens from a Penpot file."""
        file_data = self.get_file_data(file_id)

        tokens = {
            "colors": self.extract_colors(file_data),
            "typography": self.extract_typography(file_data),
            "spacing": self.extract_spacing(file_data),
            "shadows": self.extract_shadows(file_data),
            "borders": self.extract_borders(file_data),
            "radii": self.extract_radii(file_data),
            "breakpoints": self.extract_breakpoints(file_data)
        }

        return tokens

    def get_file_data(self, file_id: str) -> Dict[str, Any]:
        """Fetch file data from Penpot API."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.client.get(
            f"{self.api_endpoint}/files/{file_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def extract_colors(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract color tokens from file data."""
        colors = []

        # Extract from library colors
        for library in file_data.get("data", {}).get("libraries", []):
            if library.get("type") == "color" or "color" in library.get("name", "").lower():
                for child in library.get("children", []):
                    if child.get("type") == "rect" and child.get("fillColor"):
                        colors.append({
                            "name": self.normalize_name(child.get("name", "Unnamed Color")),
                            "value": self.normalize_color(child["fillColor"]),
                            "opacity": child.get("fillOpacity"),
                            "description": child.get("description"),
                            "category": self.categorize_color(child["fillColor"])
                        })

        # Extract from component colors
        for component in file_data.get("data", {}).get("components", []):
            for shape in self.flatten_shapes(component):
                if shape.get("type") == "rect" and shape.get("fillColor"):
                    # Avoid duplicates
                    if not any(c["value"] == shape["fillColor"] for c in colors):
                        colors.append({
                            "name": self.normalize_name(shape.get("name", "Unnamed Color")),
                            "value": self.normalize_color(shape["fillColor"]),
                            "opacity": shape.get("fillOpacity"),
                            "category": self.categorize_color(shape["fillColor"])
                        })

        return colors

    def extract_typography(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract typography tokens from file data."""
        typography = []

        for page in file_data.get("data", {}).get("pages", []):
            for shape in self.flatten_shapes(page):
                if shape.get("type") == "text":
                    typo = {
                        "name": self.normalize_name(shape.get("name", "Unnamed Typography")),
                        "fontFamily": self.normalize_font(shape.get("fontFamily", "Inter")),
                        "fontSize": self.normalize_font_size(shape.get("fontSize", "16px")),
                        "fontWeight": str(shape.get("fontWeight", "400")),
                        "lineHeight": self.normalize_line_height(shape.get("lineHeight", "1.5")),
                        "letterSpacing": shape.get("letterSpacing"),
                        "textAlign": shape.get("textAlign", "left")
                    }
                    # Avoid duplicates
                    if not any(t["name"] == typo["name"] for t in typography):
                        typography.append(typo)

        return typography

    def extract_spacing(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract spacing tokens from file data."""
        spacing = []

        # Common spacing scale (based on 8px grid)
        common_spacing = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128]

        for value in common_spacing:
            spacing.append({
                "name": f"spacing-{value}",
                "value": f"{value}px",
                "description": f"{value}px spacing unit"
            })

        return spacing

    def extract_shadows(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract shadow tokens from file data."""
        shadows = []

        for page in file_data.get("data", {}).get("pages", []):
            for shape in self.flatten_shapes(page):
                if shape.get("type") == "rect" and shape.get("shadow"):
                    shadow = shape["shadow"]
                    formatted = self.format_shadow(shadow)
                    shadows.append({
                        "name": self.normalize_name(shape.get("name", "Unnamed Shadow")),
                        "value": formatted,
                        "description": f"Shadow: {formatted}"
                    })

        return shadows

    def extract_borders(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract border tokens from file data."""
        borders = []

        for page in file_data.get("data", {}).get("pages", []):
            for shape in self.flatten_shapes(page):
                if shape.get("strokeColor") or shape.get("strokeWidth"):
                    borders.append({
                        "name": self.normalize_name(shape.get("name", "Unnamed Border")),
                        "color": self.normalize_color(shape.get("strokeColor", "#000000")),
                        "width": f"{shape.get('strokeWidth', 1)}px",
                        "style": shape.get("strokeStyle", "solid")
                    })

        return borders

    def extract_radii(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract border radius tokens from file data."""
        radii = []

        # Common radius values
        common_radii = [0, 2, 4, 8, 12, 16, 24, 32, 9999]

        for value in common_radii:
            name = "full" if value == 9999 else str(value)
            radii.append({
                "name": f"radius-{name}",
                "value": "9999px" if value == 9999 else f"{value}px",
                "description": f"{'Full' if value == 9999 else value}px border radius"
            })

        return radii

    def extract_breakpoints(self, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract breakpoint tokens from file data."""
        return [
            {"name": "breakpoint-sm", "value": "640px", "description": "Small screens"},
            {"name": "breakpoint-md", "value": "768px", "description": "Medium screens"},
            {"name": "breakpoint-lg", "value": "1024px", "description": "Large screens"},
            {"name": "breakpoint-xl", "value": "1280px", "description": "Extra large screens"},
            {"name": "breakpoint-2xl", "value": "1536px", "description": "2x Extra large screens"}
        ]

    def flatten_shapes(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten shape tree into list."""
        shapes = []
        for child in node.get("children", []):
            shapes.append(child)
            if child.get("children"):
                shapes.extend(self.flatten_shapes(child))
        return shapes

    def normalize_name(self, name: str) -> str:
        """Normalize token name to kebab-case."""
        if not name:
            return "unnamed"
        # Convert to kebab-case
        name = re.sub(r"[\s_]+", "-", name)
        name = re.sub(r"([a-z])([A-Z])", r"\1-\2", name)
        name = re.sub(r"[^a-zA-Z0-9-]", "", name)
        return name.lower()

    def normalize_color(self, color: str) -> str:
        """Normalize color to hex format."""
        if not color:
            return "#000000"

        color = color.strip()

        # Already hex
        if color.startswith("#"):
            return color.upper() if len(color) == 7 else color[0] + color[1:].upper() + color[3:].upper()

        # RGB/RGBA
        if color.startswith("rgb"):
            match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)", color)
            if match:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return f"#{r:02X}{g:02X}{b:02X}"

        return color

    def normalize_font(self, font: str) -> str:
        """Normalize font family to Google Fonts format."""
        if not font:
            return "Inter"

        # Common font mappings
        font_map = {
            "SF Pro Display": "Inter",
            "SF Pro Text": "Inter",
            "Helvetica Neue": "Inter",
            "Roboto": "Roboto",
            "Open Sans": "Open Sans",
            "Lato": "Lato",
            "Poppins": "Poppins"
        }

        return font_map.get(font, font)

    def normalize_font_size(self, size: str) -> str:
        """Normalize font size to px format."""
        if not size:
            return "16px"
        if isinstance(size, (int, float)):
            return f"{size}px"
        if isinstance(size, str):
            if size.endswith("px") or size.endswith("pt"):
                return size
            try:
                float(size)
                return f"{size}px"
            except ValueError:
                return size
        return "16px"

    def normalize_line_height(self, height: str) -> str:
        """Normalize line height to unitless or px format."""
        if not height:
            return "1.5"
        if isinstance(height, (int, float)):
            return str(height)
        return str(height)

    def categorize_color(self, color: str) -> str:
        """Categorize color based on its value."""
        color_lower = color.lower()

        # Check name hints if available
        if "primary" in color_lower:
            return "primary"
        elif "secondary" in color_lower:
            return "secondary"
        elif "neutral" in color_lower or "gray" in color_lower or "grey" in color_lower:
            return "neutral"
        elif "success" in color_lower or "green" in color_lower:
            return "functional"
        elif "danger" in color_lower or "error" in color_lower or "red" in color_lower:
            return "functional"
        elif "warning" in color_lower or "amber" in color_lower or "yellow" in color_lower:
            return "functional"

        return "semantic"

    def format_shadow(self, shadow: Dict[str, Any]) -> str:
        """Format shadow object to CSS string."""
        x = shadow.get("x", 0)
        y = shadow.get("y", 4)
        blur = shadow.get("blur", 8)
        spread = shadow.get("spread", 0)
        color = self.normalize_color(shadow.get("color", "#000"))
        opacity = shadow.get("opacity", 0.1)

        if opacity != 1:
            return f"{x}px {y}px {blur}px {spread}px {color}{int(opacity * 255):02X}"
        return f"{x}px {y}px {blur}px {spread}px {color}"


class PenpotAPIClient:
    """HTTP client for Penpot API."""

    def __init__(self, api_key: Optional[str] = None, api_endpoint: str = "https://api.penpot.app/v1"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.client = httpx.Client(timeout=30.0)

    def get(self, path: str) -> Dict[str, Any]:
        """Make GET request to Penpot API."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.client.get(f"{self.api_endpoint}{path}", headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to Penpot API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.client.post(
            f"{self.api_endpoint}{path}",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
