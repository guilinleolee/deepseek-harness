#!/usr/bin/env python3
"""
Browser Artifacts Capture Script

Usage:
    python capture_browser_artifacts.py --project-root . --output-dir .debug/browser-artifacts

This script captures browser debugging artifacts including:
- Console logs
- Network requests
- Screenshots
- DOM snapshots
- Performance metrics

Inspired by GSD-2 debug-like-expert and omnidebug-autopilot.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def ensure_output_dir(output_dir: str) -> Path:
    """Ensure output directory exists."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def capture_console_logs(output_dir: Path, project_root: str) -> dict:
    """Capture console logs from browser DevTools."""
    console_file = output_dir / "console_logs.json"

    # This would typically be done via Playwright/Puppeteer CDP
    # For now, we create a template structure
    console_data = {
        "timestamp": datetime.now().isoformat(),
        "logs": [],
        "errors": [],
        "warnings": [],
        "source": "browser_devtools",
        "note": "Use Playwright/Puppeteer CDP to capture actual console logs"
    }

    with open(console_file, "w", encoding="utf-8") as f:
        json.dump(console_data, f, indent=2)

    return {
        "file": str(console_file),
        "captured": False,
        "note": "Requires Playwright/Puppeteer integration"
    }


def capture_network_requests(output_dir: Path, project_root: str) -> dict:
    """Capture network requests from browser DevTools."""
    network_file = output_dir / "network_requests.json"

    # This would typically be done via Playwright/Puppeteer CDP
    network_data = {
        "timestamp": datetime.now().isoformat(),
        "requests": [],
        "failed_requests": [],
        "source": "browser_devtools",
        "note": "Use Playwright/Puppeteer CDP to capture actual network requests"
    }

    with open(network_file, "w", encoding="utf-8") as f:
        json.dump(network_data, f, indent=2)

    return {
        "file": str(network_file),
        "captured": False,
        "note": "Requires Playwright/Puppeteer integration"
    }


def capture_screenshot(output_dir: Path, project_root: str) -> dict:
    """Capture screenshot of the browser page."""
    screenshot_file = output_dir / "screenshot.png"

    # Check if Playwright is available
    try:
        result = subprocess.run(
            ["npx", "playwright", "--version"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        if result.returncode == 0:
            return {
                "file": str(screenshot_file),
                "captured": False,
                "playwright_available": True,
                "note": "Run: npx playwright screenshot <url> " + str(screenshot_file)
            }
    except Exception:
        pass

    return {
        "file": str(screenshot_file),
        "captured": False,
        "playwright_available": False,
        "note": "Install Playwright: npm install -D @playwright/test"
    }


def capture_dom_snapshot(output_dir: Path, project_root: str) -> dict:
    """Capture DOM snapshot."""
    dom_file = output_dir / "dom_snapshot.html"

    dom_data = {
        "timestamp": datetime.now().isoformat(),
        "file": str(dom_file),
        "captured": False,
        "note": "Use Playwright page.content() or document.documentElement.outerHTML"
    }

    with open(dom_file, "w", encoding="utf-8") as f:
        f.write("<!-- DOM snapshot placeholder -->\n")
        f.write("<!-- Use Playwright/Puppeteer to capture actual DOM -->\n")

    return dom_data


def capture_performance_metrics(output_dir: Path, project_root: str) -> dict:
    """Capture performance metrics."""
    perf_file = output_dir / "performance_metrics.json"

    perf_data = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "domContentLoaded": None,
            "load": None,
            "firstPaint": None,
            "firstContentfulPaint": None,
            "largestContentfulPaint": None,
            "cumulativeLayoutShift": None,
            "totalBlockingTime": None
        },
        "note": "Use Playwright page.metrics() or Performance API"
    }

    with open(perf_file, "w", encoding="utf-8") as f:
        json.dump(perf_data, f, indent=2)

    return {
        "file": str(perf_file),
        "captured": False
    }


def capture_test_output(output_dir: Path, project_root: str) -> dict:
    """Capture test output if available."""
    test_output_file = output_dir / "test_output.log"

    # Check for common test output locations
    test_output_dirs = [
        "test-results",
        "playwright-report",
        "coverage",
        ".nyc_output"
    ]

    captured = []
    for test_dir in test_output_dirs:
        test_path = Path(project_root) / test_dir
        if test_path.exists():
            dest_path = output_dir / test_dir
            if test_path.is_dir():
                shutil.copytree(test_path, dest_path, dirs_exist_ok=True)
                captured.append(test_dir)

    if captured:
        return {
            "captured": True,
            "directories": captured
        }

    return {
        "captured": False,
        "note": "No test output directories found"
    }


def capture_environment_info(output_dir: Path, project_root: str) -> dict:
    """Capture environment information."""
    env_file = output_dir / "environment.json"

    env_data = {
        "timestamp": datetime.now().isoformat(),
        "project_root": project_root,
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd()
    }

    # Try to get Node.js version
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            env_data["node_version"] = result.stdout.strip()
    except Exception:
        pass

    # Try to get npm version
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            env_data["npm_version"] = result.stdout.strip()
    except Exception:
        pass

    with open(env_file, "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent=2)

    return {
        "file": str(env_file),
        "captured": True
    }


def capture_artifacts(project_root: str, output_dir: str) -> dict:
    """
    Capture all browser debugging artifacts.

    Args:
        project_root: Path to project root
        output_dir: Directory to save artifacts

    Returns:
        dict with capture results
    """
    output_path = ensure_output_dir(output_dir)

    print(f"\n{'='*60}")
    print(f"Browser Artifacts Capture")
    print(f"{'='*60}")
    print(f"Project: {project_root}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")

    results = {
        "project_root": project_root,
        "output_dir": str(output_path),
        "timestamp": datetime.now().isoformat(),
        "artifacts": {}
    }

    # Capture each artifact type
    print("Capturing artifacts...")

    print("  - Console logs...")
    results["artifacts"]["console_logs"] = capture_console_logs(output_path, project_root)

    print("  - Network requests...")
    results["artifacts"]["network_requests"] = capture_network_requests(output_path, project_root)

    print("  - Screenshot...")
    results["artifacts"]["screenshot"] = capture_screenshot(output_path, project_root)

    print("  - DOM snapshot...")
    results["artifacts"]["dom_snapshot"] = capture_dom_snapshot(output_path, project_root)

    print("  - Performance metrics...")
    results["artifacts"]["performance_metrics"] = capture_performance_metrics(output_path, project_root)

    print("  - Test output...")
    results["artifacts"]["test_output"] = capture_test_output(output_path, project_root)

    print("  - Environment info...")
    results["artifacts"]["environment"] = capture_environment_info(output_path, project_root)

    # Save summary
    summary_file = output_path / "capture_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Capture Complete")
    print(f"{'='*60}")
    print(f"Artifacts saved to: {output_path}")
    print(f"Summary: {summary_file}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Capture browser debugging artifacts"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to project root"
    )
    parser.add_argument(
        "--output-dir",
        default=".debug/browser-artifacts",
        help="Directory to save artifacts"
    )

    args = parser.parse_args()

    results = capture_artifacts(
        project_root=os.path.abspath(args.project_root),
        output_dir=args.output_dir
    )

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)