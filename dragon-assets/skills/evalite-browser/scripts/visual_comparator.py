#!/usr/bin/env python3
"""
evalite-browser Visual Comparator

Visual regression testing engine using Pillow for screenshot comparison
and diff highlighting. Supports baseline comparison, pixel-level diff,
and HTML report generation.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from PIL import Image, ImageDraw, ImageChops, ImageStat
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

console = Console()


@dataclass
class VisualDiffResult:
    """Result of visual comparison."""
    baseline_path: str
    current_path: str
    diff_path: Optional[str]
    has_diff: bool
    diff_percentage: float
    diff_regions: List[Dict[str, Any]] = field(default_factory=list)
    threshold: float = 0.1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_path": self.baseline_path,
            "current_path": self.current_path,
            "diff_path": self.diff_path,
            "has_diff": self.has_diff,
            "diff_percentage": self.diff_percentage,
            "diff_regions": self.diff_regions,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
        }


class VisualComparator:
    """
    Visual regression testing engine.

    Compares baseline screenshots with current screenshots to detect
    visual regressions. Uses pixel-level comparison with configurable
    threshold and diff highlighting.
    """

    def __init__(
        self,
        baseline_dir: str = "./baseline",
        current_dir: str = "./current",
        output_dir: str = "./reports/diffs",
        threshold: float = 0.1,
        diff_highlight: bool = True,
    ):
        self.baseline_dir = Path(baseline_dir)
        self.current_dir = Path(current_dir)
        self.output_dir = Path(output_dir)
        self.threshold = threshold
        self.diff_highlight = diff_highlight

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compare(
        self,
        baseline_name: str,
        current_name: Optional[str] = None,
        output_name: Optional[str] = None,
    ) -> VisualDiffResult:
        """
        Compare baseline and current screenshots.

        Args:
            baseline_name: Name of baseline screenshot file
            current_name: Name of current screenshot (defaults to baseline_name)
            output_name: Name for diff output file

        Returns:
            VisualDiffResult with comparison details
        """
        baseline_path = self.baseline_dir / baseline_name
        if current_name:
            current_path = self.current_dir / current_name
        else:
            current_path = self.current_dir / baseline_name

        if not baseline_path.exists():
            return VisualDiffResult(
                baseline_path=str(baseline_path),
                current_path=str(current_path),
                diff_path=None,
                has_diff=True,
                diff_percentage=100.0,
                threshold=self.threshold,
            )

        if not current_path.exists():
            return VisualDiffResult(
                baseline_path=str(baseline_path),
                current_path=str(current_path),
                diff_path=None,
                has_diff=True,
                diff_percentage=100.0,
                threshold=self.threshold,
            )

        # Load images
        baseline_img = Image.open(baseline_path)
        current_img = Image.open(current_path)

        # Convert to RGB if needed
        if baseline_img.mode != "RGB":
            baseline_img = baseline_img.convert("RGB")
        if current_img.mode != "RGB":
            current_img = current_img.convert("RGB")

        # Check dimensions
        if baseline_img.size != current_img.size:
            # Resize current to match baseline
            current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

        # Calculate diff
        diff_percentage, diff_regions = self._calculate_diff(
            baseline_img, current_img
        )

        # Generate diff image if enabled and diff detected
        diff_path = None
        if self.diff_highlight and diff_percentage > 0:
            output_name = output_name or f"diff_{baseline_name}"
            diff_path = self._generate_diff_image(
                baseline_img, current_img, output_name
            )

        has_diff = diff_percentage > (self.threshold * 100)

        return VisualDiffResult(
            baseline_path=str(baseline_path),
            current_path=str(current_path),
            diff_path=diff_path,
            has_diff=has_diff,
            diff_percentage=diff_percentage,
            diff_regions=diff_regions,
            threshold=self.threshold,
        )

    def _calculate_diff(
        self, img1: Image.Image, img2: Image.Image
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate pixel-level difference between two images.

        Returns:
            Tuple of (diff_percentage, list of diff regions)
        """
        # Convert to grayscale for comparison
        gray1 = ImageChops.grayscale(img1)
        gray2 = ImageChops.grayscale(img2)

        # Calculate absolute difference
        diff = ImageChops.difference(gray1, gray2)

        # Get pixel count
        width, height = diff.size
        total_pixels = width * height

        # Get diff pixels (non-zero differences)
        diff_data = list(diff.getdata())
        diff_pixels = sum(1 for p in diff_data if p > 0)

        # Calculate percentage
        diff_percentage = (diff_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        # Find diff regions (contiguous areas)
        diff_regions = self._find_diff_regions(diff, threshold=10)

        return diff_percentage, diff_regions

    def _find_diff_regions(
        self, diff_img: Image.Image, threshold: int = 10
    ) -> List[Dict[str, Any]]:
        """Find contiguous regions of difference in the diff image."""
        regions = []
        width, height = diff_img.size
        visited = set()

        # Scan for diff pixels
        for y in range(0, height, 20):  # Sample every 20 pixels for speed
            for x in range(0, width, 20):
                if (x, y) in visited:
                    continue

                pixel = diff_img.getpixel((x, y))
                if isinstance(pixel, tuple):
                    pixel = pixel[0]

                if pixel > threshold:
                    # Found a diff region - expand to find bounds
                    region = self._expand_region(diff_img, x, y, threshold, visited)
                    if region:
                        regions.append(region)

        return regions[:10]  # Limit to top 10 regions

    def _expand_region(
        self,
        diff_img: Image.Image,
        start_x: int,
        start_y: int,
        threshold: int,
        visited: set,
    ) -> Optional[Dict[str, Any]]:
        """Expand from a starting point to find region bounds."""
        width, height = diff_img.size
        min_x, min_y = start_x, start_y
        max_x, max_y = start_x, start_y
        pixels = 0

        # Simple flood fill
        stack = [(start_x, start_y)]
        checked = set()

        while stack and pixels < 1000:  # Limit region size
            x, y = stack.pop()
            if (x, y) in checked:
                continue
            checked.add((x, y))

            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            pixel = diff_img.getpixel((x, y))
            if isinstance(pixel, tuple):
                pixel = pixel[0]

            if pixel > threshold:
                pixels += 1
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

                # Add neighbors
                stack.append((x + 20, y))
                stack.append((x - 20, y))
                stack.append((x, y + 20))
                stack.append((x, y - 20))

        if pixels < 5:  # Ignore tiny regions
            return None

        return {
            "x": min_x,
            "y": min_y,
            "width": max_x - min_x,
            "height": max_y - min_y,
            "pixel_count": pixels,
        }

    def _generate_diff_image(
        self,
        baseline: Image.Image,
        current: Image.Image,
        output_name: str,
    ) -> str:
        """Generate a diff image with highlighting."""
        # Calculate diff
        gray1 = ImageChops.grayscale(baseline)
        gray2 = ImageChops.grayscale(current)
        diff = ImageChops.difference(gray1, gray2)

        # Create output with diff highlighting
        output_img = Image.new("RGB", baseline.size, (255, 255, 255))
        draw = ImageDraw.Draw(output_img)

        # Paste baseline on left
        output_img.paste(baseline, (0, 0))

        # Paste current on right
        output_img.paste(current, (baseline.size[0], 0))

        # Calculate diff image for middle section
        diff_resized = diff.resize((baseline.size[0], baseline.size[1]), Image.NEAREST)
        diff_rgb = Image.new("RGB", baseline.size)

        for y in range(baseline.size[1]):
            for x in range(baseline.size[0]):
                pixel = diff_resized.getpixel((x, y))
                if isinstance(pixel, tuple):
                    pixel = pixel[0]

                if pixel > 5:
                    # Red for differences
                    intensity = min(255, pixel * 4)
                    diff_rgb.putpixel((x, y), (255, intensity, intensity))
                else:
                    diff_rgb.putpixel((x, y), (200, 200, 200))

        # Paste diff in middle
        output_img.paste(diff_rgb, (baseline.size[0] * 2, 0))

        # Add labels
        draw = ImageDraw.Draw(output_img)
        draw.text((10, 10), "BASELINE", fill=(0, 255, 0))
        draw.text(
            (baseline.size[0] + 10, 10), "CURRENT", fill=(0, 255, 0)
        )
        draw.text(
            (baseline.size[0] * 2 + 10, 10), "DIFF", fill=(255, 0, 0)
        )

        # Save
        output_path = self.output_dir / output_name
        output_img.save(output_path)

        return str(output_path)

    def batch_compare(
        self, pairs: List[Tuple[str, str]]
    ) -> List[VisualDiffResult]:
        """Compare multiple image pairs."""
        results = []
        for baseline_name, current_name in track(
            pairs, description="Comparing screenshots..."
        ):
            result = self.compare(baseline_name, current_name)
            results.append(result)
        return results

    def generate_report(
        self, results: List[VisualDiffResult], output_path: str = "visual-report.html"
    ) -> None:
        """Generate HTML visual comparison report."""
        timestamp = datetime.now().isoformat()

        passed = sum(1 for r in results if not r.has_diff)
        failed = len(results) - passed

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>evalite-browser Visual Regression Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
        .stat.passed {{ border-left: 4px solid #22c55e; }}
        .stat.failed {{ border-left: 4px solid #ef4444; }}
        .stat .number {{ font-size: 48px; font-weight: bold; }}
        .stat.passed .number {{ color: #22c55e; }}
        .stat.failed .number {{ color: #ef4444; }}
        .test {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 16px; }}
        .test.passed {{ border-left: 4px solid #22c55e; }}
        .test.failed {{ border-left: 4px solid #ef4444; }}
        .comparison {{ display: flex; gap: 10px; margin: 10px 0; }}
        .comparison img {{ max-width: 32%; border: 1px solid #ddd; border-radius: 4px; }}
        .diff-info {{ color: #ef4444; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>evalite-browser Visual Regression Report</h1>
        <p>Generated: {timestamp}</p>
    </div>
    <div class="summary">
        <div class="stat passed">
            <div class="number">{passed}</div>
            <div>Passed</div>
        </div>
        <div class="stat failed">
            <div class="number">{failed}</div>
            <div>Failed</div>
        </div>
    </div>
"""

        for result in results:
            status = "passed" if not result.has_diff else "failed"
            status_text = "PASSED" if not result.has_diff else "FAILED"

            html += f"""
    <div class="test {status}">
        <h3>{Path(result.baseline_path).name} - <span class="diff-info">{status_text}</span></h3>
        <p>Diff: {result.diff_percentage:.2f}% (threshold: {result.threshold * 100:.0f}%)</p>
        <div class="comparison">
"""

            html += f'<img src="file://{result.baseline_path}" alt="Baseline" />'
            html += f'<img src="file://{result.current_path}" alt="Current" />'

            if result.diff_path:
                html += f'<img src="file://{result.diff_path}" alt="Diff" />'

            html += "</div>"

            if result.diff_regions:
                html += "<details><summary>Diff Regions</summary><ul>"
                for region in result.diff_regions:
                    html += f"<li>Region: x={region['x']}, y={region['y']}, "
                    html += f"w={region['width']}, h={region['height']} "
                    html += f"({region['pixel_count']} pixels)</li>"
                html += "</ul></details>"

            html += "</div>"

        html += """
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)


# CLI Commands
@click.group()
def cli():
    """Visual regression testing CLI."""
    pass


@cli.command()
@click.option("--baseline", "-b", required=True, help="Baseline screenshot path or directory")
@click.option("--compare", "-c", required=True, help="Current screenshot path or directory")
@click.option("--output", "-o", default="./reports/diffs", help="Output directory")
@click.option("--threshold", "-t", default=0.1, help="Diff threshold (0-1)")
@click.option("--name", "-n", help="Specific screenshot name to compare")
@click.option("--report", "-r", help="Generate HTML report to path")
def compare(baseline: str, compare: str, output: str, threshold: float, name: str, report: str):
    """Compare baseline and current screenshots."""
    comparator = VisualComparator(
        baseline_dir=baseline,
        current_dir=compare,
        output_dir=output,
        threshold=threshold,
    )

    if name:
        # Compare specific image
        result = comparator.compare(name)
        _print_result(result)
    else:
        # Compare all images in baseline directory
        baseline_path = Path(baseline)
        if not baseline_path.exists():
            console.print(f"[red]Baseline directory not found: {baseline}[/red]")
            return

        pairs = [(f.name, f.name) for f in baseline_path.glob("*.png")]
        if not pairs:
            pairs = [(f.name, f.name) for f in baseline_path.glob("*.jpg")]

        if not pairs:
            console.print("[yellow]No screenshots found to compare[/yellow]")
            return

        results = comparator.batch_compare(pairs)

        table = Table(title="Visual Comparison Results")
        table.add_column("Screenshot", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Diff %", style="yellow")

        for result in results:
            status = "[green]PASS[/green]" if not result.has_diff else "[red]FAIL[/red]"
            table.add_row(
                Path(result.baseline_path).name,
                status,
                f"{result.diff_percentage:.2f}%",
            )

        console.print(table)

        if report:
            comparator.generate_report(results, report)
            console.print(f"[green]Report saved to: {report}[/green]")

        passed = sum(1 for r in results if not r.has_diff)
        failed = len(results) - passed
        console.print(f"\n[bold]Summary:[/bold] {passed} passed, {failed} failed")


@cli.command()
@click.option("--baseline", "-b", required=True, help="First screenshot")
@click.option("--current", "-c", required=True, help="Second screenshot")
@click.option("--output", "-o", required=True, help="Output diff image path")
@click.option("--highlight/--no-highlight", default=True, help="Highlight diff regions")
def diff(baseline: str, current: str, output: str, highlight: bool):
    """Generate diff image between two screenshots."""
    comparator = VisualComparator(diff_highlight=highlight)
    result = comparator.compare(baseline, current, output_name=Path(output).name)

    if result.diff_path:
        console.print(f"[green]Diff image saved to: {result.diff_path}[/green]")
    else:
        console.print("[yellow]No diff detected[/yellow]")


def _print_result(result: VisualDiffResult):
    """Print a single comparison result."""
    status = "[green]PASS[/green]" if not result.has_diff else "[red]FAIL[/red]"

    console.print(Panel.fit(
        f"[bold]{Path(result.baseline_path).name}[/bold]\n"
        f"Status: {status}\n"
        f"Diff: {result.diff_percentage:.2f}% "
        f"(threshold: {result.threshold * 100:.0f}%)\n"
        f"Baseline: {result.baseline_path}\n"
        f"Current: {result.current_path}",
        title="Visual Comparison Result",
        border_style="green" if not result.has_diff else "red",
    ))

    if result.diff_path:
        console.print(f"[cyan]Diff image: {result.diff_path}[/cyan]")


if __name__ == "__main__":
    cli()
