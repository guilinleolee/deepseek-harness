#!/usr/bin/env python3
"""
Browser Issue Reproduction Script

Usage:
    python repro_browser_issue.py --project-root . --repro-cmd "playwright test tests/bug.spec.ts" --expect fail --runs 2

This script reproduces browser issues deterministically and captures debugging artifacts.
Inspired by GSD-2 debug-like-expert and omnidebug-autopilot.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def run_command(cmd: str, cwd: str, timeout: int = 300) -> dict:
    """Run a shell command and return result."""
    start_time = datetime.now()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        end_time = datetime.now()
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_seconds": (end_time - start_time).total_seconds(),
            "command": cmd
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "duration_seconds": timeout,
            "command": cmd
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration_seconds": 0,
            "command": cmd
        }


def reproduce_issue(
    project_root: str,
    repro_cmd: str,
    expect: str = "fail",
    runs: int = 1,
    timeout: int = 300
) -> dict:
    """
    Reproduce a browser issue multiple times.

    Args:
        project_root: Path to project root
        repro_cmd: Command to reproduce the issue
        expect: Expected result ('fail' or 'pass')
        runs: Number of times to run
        timeout: Timeout in seconds

    Returns:
        dict with reproduction results
    """
    results = []

    print(f"\n{'='*60}")
    print(f"Browser Issue Reproduction")
    print(f"{'='*60}")
    print(f"Project: {project_root}")
    print(f"Command: {repro_cmd}")
    print(f"Expect: {expect}")
    print(f"Runs: {runs}")
    print(f"{'='*60}\n")

    for i in range(1, runs + 1):
        print(f"\n--- Run {i}/{runs} ---")
        result = run_command(repro_cmd, project_root, timeout)

        # Check if result matches expectation
        actual = "fail" if not result["success"] else "pass"
        matches = actual == expect

        result["run_number"] = i
        result["expected"] = expect
        result["actual"] = actual
        result["matches_expectation"] = matches

        results.append(result)

        print(f"Result: {actual} (expected: {expect})")
        print(f"Duration: {result['duration_seconds']:.2f}s")

        if result["stderr"]:
            print(f"Stderr: {result['stderr'][:500]}...")

        if not matches:
            print(f"⚠️  Result does not match expectation!")

    # Summary
    success_rate = sum(1 for r in results if r["matches_expectation"]) / len(results)

    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Total runs: {len(results)}")
    print(f"Matches expectation: {sum(1 for r in results if r['matches_expectation'])}")
    print(f"Success rate: {success_rate * 100:.1f}%")

    return {
        "project_root": project_root,
        "repro_cmd": repro_cmd,
        "expect": expect,
        "runs": runs,
        "results": results,
        "success_rate": success_rate,
        "timestamp": datetime.now().isoformat()
    }


def save_results(results: dict, output_path: Optional[str] = None):
    """Save results to JSON file."""
    if output_path is None:
        output_dir = Path(results["project_root"]) / ".debug"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"repro_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce browser issues deterministically"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to project root"
    )
    parser.add_argument(
        "--repro-cmd",
        required=True,
        help="Command to reproduce the issue"
    )
    parser.add_argument(
        "--expect",
        choices=["fail", "pass"],
        default="fail",
        help="Expected result (default: fail)"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs (default: 1)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path"
    )

    args = parser.parse_args()

    results = reproduce_issue(
        project_root=os.path.abspath(args.project_root),
        repro_cmd=args.repro_cmd,
        expect=args.expect,
        runs=args.runs,
        timeout=args.timeout
    )

    save_results(results, args.output)

    # Exit with error if success rate is low
    if results["success_rate"] < 0.5:
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)