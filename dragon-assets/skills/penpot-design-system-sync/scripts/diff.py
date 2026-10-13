#!/usr/bin/env python3
"""
Penpot Design System Sync - Token Diff Module
Compares two versions of design tokens and generates change reports.
"""

import json
from typing import Any, Dict, List, Optional


class TokenDiffer:
    """Compare two versions of design tokens."""

    def compare(self, before_file: str, after_file: str) -> Dict[str, Any]:
        """Compare two token files and generate diff report."""
        with open(before_file, "r", encoding="utf-8") as f:
            before = json.load(f)

        with open(after_file, "r", encoding="utf-8") as f:
            after = json.load(f)

        return self.compare_tokens(before, after)

    def compare_tokens(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two token objects."""
        report = {
            "added": [],
            "removed": [],
            "modified": [],
            "breaking": [],
            "summary": {
                "added_count": 0,
                "removed_count": 0,
                "modified_count": 0,
                "breaking_count": 0
            }
        }

        # Compare colors
        self._compare_category(
            before.get("colors", []),
            after.get("colors", []),
            "colors",
            report
        )

        # Compare typography
        self._compare_category(
            before.get("typography", []),
            after.get("typography", []),
            "typography",
            report
        )

        # Compare spacing
        self._compare_category(
            before.get("spacing", []),
            after.get("spacing", []),
            "spacing",
            report
        )

        # Compare shadows
        self._compare_category(
            before.get("shadows", []),
            after.get("shadows", []),
            "shadows",
            report
        )

        # Update summary counts
        report["summary"]["added_count"] = len(report["added"])
        report["summary"]["removed_count"] = len(report["removed"])
        report["summary"]["modified_count"] = len(report["modified"])
        report["summary"]["breaking_count"] = len(report["breaking"])

        return report

    def _compare_category(
        self,
        before_items: List[Dict[str, Any]],
        after_items: List[Dict[str, Any]],
        category: str,
        report: Dict[str, Any]
    ):
        """Compare a category of tokens."""
        before_map = {item["name"]: item for item in before_items}
        after_map = {item["name"]: item for item in after_items}

        before_names = set(before_map.keys())
        after_names = set(after_map.keys())

        # Find added tokens
        for name in after_names - before_names:
            item = after_map[name]
            report["added"].append({
                "category": category,
                "name": name,
                "value": item.get("value") or item.get("fontFamily") or item.get("width"),
                "description": item.get("description")
            })

            # Check if it's a semantic token (breaking change if removed)
            if item.get("category") in ["primary", "secondary", "semantic"]:
                report["breaking"].append({
                    "type": "semantic_added",
                    "name": name,
                    "severity": "medium"
                })

        # Find removed tokens
        for name in before_names - after_names:
            item = before_map[name]
            report["removed"].append({
                "category": category,
                "name": name,
                "value": item.get("value") or item.get("fontFamily") or item.get("width"),
                "severity": "high" if item.get("category") in ["primary", "secondary", "semantic"] else "medium"
            })

            # Semantic/functional tokens are breaking changes
            if item.get("category") in ["primary", "secondary", "semantic", "functional"]:
                report["breaking"].append({
                    "type": "semantic_removed",
                    "name": name,
                    "severity": "high"
                })

        # Find modified tokens
        for name in before_names & after_names:
            before_item = before_map[name]
            after_item = after_map[name]

            changes = self._find_changes(before_item, after_item)
            if changes:
                report["modified"].append({
                    "category": category,
                    "name": name,
                    "changes": changes
                })

                # Check if the change is breaking
                if self._is_breaking_change(category, changes):
                    report["breaking"].append({
                        "type": "semantic_modified",
                        "name": name,
                        "changes": changes,
                        "severity": "high"
                    })

    def _find_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find specific changes between two token items."""
        changes = []

        # Color-specific changes
        if "value" in before and "value" in after and before["value"] != after["value"]:
            changes.append({
                "field": "value",
                "before": before["value"],
                "after": after["value"]
            })

        if "opacity" in before and "opacity" in after and before["opacity"] != after["opacity"]:
            changes.append({
                "field": "opacity",
                "before": before["opacity"],
                "after": after["opacity"]
            })

        # Typography-specific changes
        for field in ["fontFamily", "fontSize", "fontWeight", "lineHeight"]:
            if field in before and field in after and before[field] != after[field]:
                changes.append({
                    "field": field,
                    "before": before[field],
                    "after": after[field]
                })

        return changes

    def _is_breaking_change(self, category: str, changes: List[Dict[str, Any]]) -> bool:
        """Determine if a change is breaking."""
        # Color value changes in semantic categories are breaking
        for change in changes:
            if change["field"] == "value" and category == "colors":
                return True
            # Typography changes are usually breaking
            if category == "typography" and change["field"] in ["fontFamily", "fontSize"]:
                return True

        return False

    def format_report(self, report: Dict[str, Any]) -> str:
        """Format diff report as readable text."""
        lines = ["# Design Token Diff Report", ""]

        # Summary
        lines.append("## Summary")
        lines.append(f"- Added: {report['summary']['added_count']}")
        lines.append(f"- Removed: {report['summary']['removed_count']}")
        lines.append(f"- Modified: {report['summary']['modified_count']}")
        lines.append(f"- Breaking Changes: {report['summary']['breaking_count']}")
        lines.append("")

        # Breaking changes (highest priority)
        if report["breaking"]:
            lines.append("## Breaking Changes")
            for item in report["breaking"]:
                lines.append(f"- **[{item['type']}]** {item['name']} (severity: {item['severity']})")
            lines.append("")

        # Added
        if report["added"]:
            lines.append("## Added")
            for item in report["added"]:
                lines.append(f"- `{item['category']}.{item['name']}` = {item['value']}")
            lines.append("")

        # Removed
        if report["removed"]:
            lines.append("## Removed")
            for item in report["removed"]:
                lines.append(f"- `{item['category']}.{item['name']}` (severity: {item['severity']})")
            lines.append("")

        # Modified
        if report["modified"]:
            lines.append("## Modified")
            for item in report["modified"]:
                lines.append(f"- `{item['category']}.{item['name']}`")
                for change in item["changes"]:
                    lines.append(f"  - {change['field']}: {change['before']} → {change['after']}")
            lines.append("")

        return "\n".join(lines)
