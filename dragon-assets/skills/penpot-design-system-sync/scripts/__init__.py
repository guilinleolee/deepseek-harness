#!/usr/bin/env python3
"""
Penpot Design System Sync - Core Module
Main sync orchestration and API client.
"""

import json
import httpx
from pathlib import Path
from typing import Any, Dict, List, Optional

from extract import TokenExtractor
from transform import TokenTransformer


class PenpotSync:
    """Main Penpot Design System Sync orchestrator."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: str = "https://api.penpot.app/v1"
    ):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.extractor = TokenExtractor(api_key, api_endpoint)
        self.client = httpx.Client(timeout=30.0)

    def extract_tokens(self, file_id: str) -> Dict[str, Any]:
        """Extract design tokens from Penpot file."""
        return self.extractor.extract_tokens(file_id)

    def transform(
        self,
        tokens: Dict[str, Any],
        format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Transform tokens to specified format."""
        transformer = TokenTransformer(tokens)
        return transformer.transform(format, options or {})

    def export(
        self,
        tokens: Dict[str, Any],
        formats: List[str],
        output_dir: str = "./design-system"
    ) -> Dict[str, str]:
        """Export tokens to multiple formats."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}

        for format in formats:
            transformer = TokenTransformer(tokens)
            content = transformer.transform(format)

            # Determine file extension
            ext_map = {
                "json": ".json",
                "css": ".css",
                "scss": ".scss",
                "ios": ".swift",
                "android": ".xml",
                "yaml": ".yaml",
                "tailwind": ".config.js"
            }

            ext = ext_map.get(format, ".txt")
            filename = f"tokens{ext}"
            filepath = output_path / format / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            results[format] = str(filepath)

        return results

    def get_current_file(self) -> Dict[str, Any]:
        """Get current file information."""
        return self._get("/api/current-file")

    def get_file_data(self, file_id: str) -> Dict[str, Any]:
        """Get file data."""
        return self._get(f"/files/{file_id}")

    def _get(self, path: str) -> Dict[str, Any]:
        """Make GET request."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.client.get(
            f"{self.api_endpoint}{path}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
