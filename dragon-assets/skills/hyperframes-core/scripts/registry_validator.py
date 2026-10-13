#!/usr/bin/env python3
"""
Registry Component Validator
验证 Registry 组件的完整性和一致性

用法:
    python3 registry_validator.py
    python3 registry_validator.py --check-all
    python3 registry_validator.py --component particle-spiral
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

REGISTRY_DIR = Path(__file__).parent.parent / "registry"
REQUIRED_FIELDS = ["id", "category", "integrationCost", "mount", "unmount"]
VALID_CATEGORIES = ["video", "text", "chart", "particle", "media"]
VALID_COSTS = ["zero", "low", "medium"]


def validate_component(name: str, content: str) -> list:
    """验证单个组件"""
    errors = []
    warnings = []

    if not re.search(r"id\s*=\s*['\"]([\w-]+)['\"]", content):
        errors.append("Missing or invalid 'id' field")

    category_match = re.search(r"category\s*=\s*['\"](\w+)['\"]", content)
    if not category_match:
        errors.append("Missing 'category' field")
    elif category_match.group(1) not in VALID_CATEGORIES:
        errors.append(f"Invalid category '{category_match.group(1)}'. "
                      f"Must be one of {VALID_CATEGORIES}")

    cost_match = re.search(r"integrationCost\s*=\s*['\"](\w+)['\"]", content)
    if not cost_match:
        errors.append("Missing 'integrationCost' field")
    elif cost_match.group(1) not in VALID_COSTS:
        errors.append(f"Invalid cost '{cost_match.group(1)}'. "
                      f"Must be one of {VALID_COSTS}")

    if "mount(" not in content and "mount():" not in content:
        errors.append("Missing 'mount()' method")

    if "unmount(" not in content and "unmount():" not in content:
        errors.append("Missing 'unmount()' method")

    if content.count("canvas") > 1 and "requiresCanvas" not in content:
        warnings.append("Component uses canvas but missing 'requiresCanvas' declaration")

    if "getContext" in content and "2d" not in content.lower():
        warnings.append("Canvas getContext should specify '2d'")

    return errors, warnings


def validate_index(index_path: Path) -> list:
    """验证 Registry 入口文件"""
    errors = []
    if not index_path.exists():
        errors.append(f"Registry index not found: {index_path}")
        return errors

    content = index_path.read_text(encoding="utf-8")

    if "window.__registry" not in content:
        errors.append("Missing 'window.__registry' initialization")

    if "forbidden_high_cost" not in content.lower() and "three.js" not in content.lower():
        pass  # OK if not using high-cost components

    return errors


def main():
    parser = argparse.ArgumentParser(description="Registry Component Validator")
    parser.add_argument("--check-all", action="store_true",
                        help="Check all components")
    parser.add_argument("--component", type=str,
                        help="Check specific component")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON format")

    args = parser.parse_args()

    results = {"passed": [], "failed": [], "warnings": []}

    if args.check_all:
        if not REGISTRY_DIR.exists():
            if args.json:
                print(json.dumps({"error": "Registry directory not found"}))
                return 1
            print(f"ERROR: Registry directory not found: {REGISTRY_DIR}")
            return 1

        for js_file in REGISTRY_DIR.glob("*.js"):
            errors, warnings = validate_component(js_file.stem, js_file.read_text())
            if errors:
                results["failed"].append({
                    "component": js_file.stem,
                    "errors": errors
                })
            elif warnings:
                results["warnings"].append({
                    "component": js_file.stem,
                    "warnings": warnings
                })
            else:
                results["passed"].append(js_file.stem)

        idx_errors = validate_index(REGISTRY_DIR / "index.js")
        if idx_errors:
            results["failed"].append({
                "component": "index.js",
                "errors": idx_errors
            })
    elif args.component:
        comp_path = REGISTRY_DIR / f"{args.component}.js"
        if not comp_path.exists():
            if args.json:
                print(json.dumps({"error": f"Component not found: {args.component}"}))
                return 1
            print(f"ERROR: Component not found: {args.component}")
            return 1

        errors, warnings = validate_component(
            args.component, comp_path.read_text()
        )
        if errors:
            results["failed"].append({
                "component": args.component,
                "errors": errors
            })
        else:
            results["passed"].append(args.component)
            if warnings:
                results["warnings"].append({
                    "component": args.component,
                    "warnings": warnings
                })
    else:
        if args.json:
            print(json.dumps({"error": "Specify --check-all or --component"}))
            return 1
        print("Registry Component Validator")
        print(f"Registry dir: {REGISTRY_DIR}")
        print("Usage:")
        print("  --check-all     Check all components")
        print("  --component ID  Check specific component")
        return 0

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Registry Validation Report")
        print(f"{'='*60}")
        print(f"  Passed:   {len(results['passed'])}")
        print(f"  Warnings: {len(results['warnings'])}")
        print(f"  Failed:   {len(results['failed'])}")

        if results["passed"]:
            print(f"\n  Passed components:")
            for name in results["passed"]:
                print(f"    ✓ {name}")

        if results["warnings"]:
            print(f"\n  Components with warnings:")
            for item in results["warnings"]:
                print(f"    ⚠ {item['component']}")
                for w in item["warnings"]:
                    print(f"        {w}")

        if results["failed"]:
            print(f"\n  Failed components:")
            for item in results["failed"]:
                print(f"    ✗ {item['component']}")
                for e in item["errors"]:
                    print(f"        {e}")

        print(f"{'='*60}\n")

    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
