#!/usr/bin/env python3
"""
evalite-browser Main CLI Runner

Provides the main CLI interface for browser-based E2E testing.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class BrowserTestRunner:
    """Main browser test runner."""

    def __init__(self, config_path: str = "configs/evalite-browser.yaml"):
        self.config = self._load_config(config_path)
        self.results: List[Dict[str, Any]] = []
        self.playwright = None
        self.browser = None
        self.context = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "browser": {
                "provider": "playwright",
                "headless": True,
                "viewport": {"width": 1280, "height": 720},
                "browsers": ["chromium"],
            },
            "visual": {"enabled": True, "baseline_dir": "./baseline", "threshold": 0.1},
            "a11y": {"enabled": True, "standard": "WCAG2AA", "rules": []},
            "interaction": {"enabled": True, "wait_for_selectors": {"timeout": 5000}},
            "reporting": {
                "formats": ["html", "json"],
                "output_dir": "./reports",
                "include_screenshots": True,
            },
        }

    def _get_browser_type(self) -> str:
        """Get browser type from config."""
        browsers = self.config.get("browser", {}).get("browsers", ["chromium"])
        return browsers[0] if browsers else "chromium"

    def _get_viewport(self) -> Dict[str, int]:
        """Get viewport from config."""
        return self.config.get("browser", {}).get(
            "viewport", {"width": 1280, "height": 720}
        )

    def launch_browser(self) -> None:
        """Launch Playwright browser."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            console.print("[red]Error: Playwright not installed. Run: pip install playwright[/red]")
            sys.exit(1)

        self.playwright = sync_playwright().start()
        browser_type = self._get_browser_type()

        console.print(f"[cyan]Launching {browser_type}...[/cyan]")
        self.browser = getattr(self.playwright, browser_type).launch(
            headless=self.config.get("browser", {}).get("headless", True)
        )

        viewport = self._get_viewport()
        self.context = self.browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]}
        )

    def close_browser(self) -> None:
        """Close browser."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def load_tests(self, tests_path: str) -> List[Dict[str, Any]]:
        """Load test cases from directory or file."""
        path = Path(tests_path)
        tests = []

        if path.is_file() and path.suffix == ".json":
            tests = [json.loads(path.read_text())]
        elif path.is_dir():
            for test_file in path.glob("*.json"):
                tests.append(json.loads(test_file.read_text()))

        return tests

    def run_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case."""
        result = {
            "name": test.get("name", "unnamed"),
            "url": test.get("url", ""),
            "passed": False,
            "steps_passed": 0,
            "steps_failed": 0,
            "assertions": [],
            "visual": None,
            "a11y": None,
            "errors": [],
        }

        page = self.context.new_page()
        url = test.get("url", "")

        if url:
            try:
                page.goto(url, wait_until="networkidle")
                result["navigation"] = "success"
            except Exception as e:
                result["errors"].append(f"Navigation failed: {e}")
                result["navigation"] = "failed"
                page.close()
                return result

        # Execute steps
        for step in test.get("steps", []):
            try:
                action = step.get("action")
                selector = step.get("selector")
                value = step.get("value")

                if action == "click" and selector:
                    page.click(selector)
                    result["steps_passed"] += 1
                elif action == "fill" and selector and value:
                    page.fill(selector, value)
                    result["steps_passed"] += 1
                elif action == "wait_for_selector" and selector:
                    timeout = step.get("timeout", 5000)
                    page.wait_for_selector(selector, timeout=timeout)
                    result["steps_passed"] += 1
                elif action == "screenshot":
                    path = step.get("path", f"screenshots/{result['name']}.png")
                    page.screenshot(path=path)
                    result["steps_passed"] += 1
            except Exception as e:
                result["steps_failed"] += 1
                result["errors"].append(f"Step {action} failed: {e}")

        # Execute assertions
        for assertion in test.get("assertions", []):
            assertion_result = {"type": assertion.get("type"), "passed": False, "details": {}}

            try:
                assertion_type = assertion.get("type")
                selector = assertion.get("selector")

                if assertion_type == "visible":
                    is_visible = page.is_visible(selector)
                    assertion_result["passed"] = is_visible
                elif assertion_type == "contains_text" and selector:
                    expected = assertion.get("text", "")
                    element_text = page.text_content(selector) or ""
                    assertion_result["passed"] = expected in element_text
                    assertion_result["details"]["expected"] = expected
                    assertion_result["details"]["actual"] = element_text[:100]

                result["assertions"].append(assertion_result)
            except Exception as e:
                assertion_result["error"] = str(e)
                result["assertions"].append(assertion_result)

        # Visual testing
        if test.get("visual", {}).get("enabled") and self.config.get("visual", {}).get("enabled"):
            try:
                from .visual_comparator import VisualComparator

                visual_config = self.config.get("visual", {})
                comparator = VisualComparator(
                    baseline_dir=visual_config.get("baseline_dir", "./baseline"),
                    threshold=visual_config.get("threshold", 0.1),
                )

                visual_name = test["visual"].get("name", result["name"])
                screenshot_path = f"screenshots/{visual_name}.png"
                page.screenshot(path=screenshot_path)

                baseline_path = f"{visual_config.get('baseline_dir', './baseline')}/{visual_name}.png"
                if Path(baseline_path).exists():
                    visual_result = comparator.compare(baseline_path, screenshot_path)
                    result["visual"] = {
                        "has_diff": visual_result.has_diff,
                        "diff_percentage": visual_result.diff_percentage,
                        "diff_image": visual_result.diff_image,
                    }
            except Exception as e:
                result["errors"].append(f"Visual test error: {e}")

        # Accessibility testing
        if test.get("a11y", {}).get("enabled") and self.config.get("a11y", {}).get("enabled"):
            try:
                from .a11y_auditor import A11yAuditor

                a11y_config = self.config.get("a11y", {})
                auditor = A11yAuditor(standard=a11y_config.get("standard", "WCAG2AA"))

                a11y_results = auditor.audit(page, rules=test["a11y"].get("rules", []))
                result["a11y"] = {
                    "violations": len(a11y_results.violations),
                    "violation_list": [
                        {"rule": v.rule_id, "description": v.description}
                        for v in a11y_results.violations
                    ],
                }
            except Exception as e:
                result["errors"].append(f"A11y test error: {e}")

        page.close()

        # Determine overall pass/fail
        result["passed"] = (
            result["steps_failed"] == 0
            and all(a.get("passed", False) for a in result["assertions"])
            and len(result["errors"]) == 0
        )

        return result

    def generate_report(self, output_dir: str, format: str = "html") -> None:
        """Generate test report."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if format == "json":
            report_path = output_path / "report.json"
            report_path.write_text(json.dumps(self.results, indent=2))
        elif format == "html":
            self._generate_html_report(output_path)
        elif format == "markdown":
            self._generate_markdown_report(output_path)

        console.print(f"[green]Report saved to {output_path}[/green]")

    def _generate_html_report(self, output_path: Path) -> None:
        """Generate HTML report."""
        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>evalite-browser Test Report</title>
    <style>
        body {{ font-family: system-ui; margin: 2rem; }}
        .summary {{ display: flex; gap: 1rem; margin-bottom: 2rem; }}
        .card {{ padding: 1rem; border-radius: 8px; flex: 1; }}
        .passed {{ background: #d4edda; }}
        .failed {{ background: #f8d7da; }}
        .test {{ border: 1px solid #ddd; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; }}
        .error {{ color: #dc3545; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <h1>evalite-browser Test Report</h1>
    <div class="summary">
        <div class="card passed">
            <h2>{passed} Passed</h2>
        </div>
        <div class="card failed">
            <h2>{failed} Failed</h2>
        </div>
    </div>
"""

        for result in self.results:
            status = "✓ Passed" if result["passed"] else "✗ Failed"
            status_class = "passed" if result["passed"] else "failed"
            html += f"""
    <div class="test">
        <h3 class="{status_class}">{status} - {result['name']}</h3>
        <p>URL: {result['url']}</p>
        <p>Steps: {result['steps_passed']} passed, {result['steps_failed']} failed</p>
"""

            if result.get("assertions"):
                html += "<h4>Assertions:</h4><ul>"
                for a in result["assertions"]:
                    icon = "✓" if a.get("passed") else "✗"
                    html += f"<li>{icon} {a.get('type')}: {a.get('details', {})}</li>"
                html += "</ul>"

            if result.get("a11y", {}).get("violations"):
                html += f"<h4>A11y Violations: {result['a11y']['violations']}</h4>"

            if result.get("visual", {}).get("has_diff"):
                html += f"<h4>Visual Diff: {result['visual']['diff_percentage']:.1%}</h4>"

            if result.get("errors"):
                html += "<h4>Errors:</h4><ul>"
                for err in result["errors"]:
                    html += f"<li class='error'>{err}</li>"
                html += "</ul>"

            html += "</div>"

        html += """
</body>
</html>"""
        (output_path / "report.html").write_text(html)

    def _generate_markdown_report(self, output_path: Path) -> None:
        """Generate Markdown report."""
        md = "# evalite-browser Test Report\n\n"

        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed
        md += f"| Passed | Failed |\n|---|---|\n| {passed} | {failed} |\n\n"

        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            md += f"\n## {status} {result['name']}\n\n"
            md += f"- **URL**: {result['url']}\n"
            md += f"- **Steps**: {result['steps_passed']} passed, {result['steps_failed']} failed\n"

            if result.get("assertions"):
                md += "\n### Assertions\n\n"
                for a in result["assertions"]:
                    icon = "✓" if a.get("passed") else "✗"
                    md += f"- {icon} {a.get('type')}\n"

            if result.get("a11y", {}).get("violations"):
                md += f"\n### A11y Violations: {result['a11y']['violations']}\n"

            if result.get("errors"):
                md += "\n### Errors\n\n"
                for err in result["errors"]:
                    md += f"- {err}\n"

        (output_path / "report.md").write_text(md)


@click.group()
def cli():
    """evalite-browser: Browser-based E2E Testing for LLM Apps."""
    pass


@cli.command()
@click.option("--url", "-u", required=True, help="Base URL to test")
@click.option("--tests", "-t", default="./tests", help="Test directory or file")
@click.option("--config", "-c", default="configs/evalite-browser.yaml", help="Config file")
@click.option("--browser", "-b", default=None, help="Browser type (chromium/firefox/webkit)")
def run(url: str, tests: str, config: str, browser: str) -> None:
    """Run browser tests."""
    console.print(Panel.fit(f"[cyan]Running tests against {url}[/cyan]", border_style="cyan"))

    runner = BrowserTestRunner(config)

    # Override browser if specified
    if browser:
        runner.config["browser"]["browsers"] = [browser]

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        progress.add_task(description="Launching browser...", total=None)

        try:
            runner.launch_browser()

            progress.add_task(description="Loading tests...", total=None)
            test_cases = runner.load_tests(tests)
            console.print(f"[cyan]Found {len(test_cases)} test(s)[/cyan]")

            # Override URL if specified
            for test in test_cases:
                if url:
                    test["url"] = url

            # Run tests
            for i, test in enumerate(test_cases):
                progress.update(
                    task_id=0, description=f"Running: {test.get('name', f'test-{i}')}"
                )
                result = runner.run_test(test)
                runner.results.append(result)

                icon = "[green]✓[/green]" if result["passed"] else "[red]✗[/red]"
                console.print(f"  {icon} {result['name']}")

            progress.update(task_id=0, description="Closing browser...")
        finally:
            runner.close_browser()

    # Generate report
    report_config = runner.config.get("reporting", {})
    output_dir = report_config.get("output_dir", "./reports")
    formats = report_config.get("formats", ["html"])

    for fmt in formats:
        runner.generate_report(output_dir, fmt)

    # Print summary
    table = Table(title="Test Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Steps", justify="right")
    table.add_column("Assertions", justify="right")

    for result in runner.results:
        status = "[green]PASSED[/green]" if result["passed"] else "[red]FAILED[/red]"
        steps = f"{result['steps_passed']}/{result['steps_passed'] + result['steps_failed']}"
        assertions = f"{sum(1 for a in result['assertions'] if a.get('passed'))}/{len(result['assertions'])}"
        table.add_row(result["name"], status, steps, assertions)

    console.print(table)


@cli.command()
@click.option("--baseline", required=True, help="Baseline screenshots directory")
@click.option("--compare", required=True, help="Current screenshots directory")
@click.option("--output", "-o", default="./reports/diffs", help="Diff output directory")
@click.option("--threshold", "-t", default=0.1, help="Diff threshold (0-1)")
def visual(baseline: str, compare: str, output: str, threshold: float) -> None:
    """Run visual regression tests."""
    console.print(Panel.fit("[cyan]Visual Regression Testing[/cyan]", border_style="cyan"))

    try:
        from .visual_comparator import VisualComparator

        comparator = VisualComparator(baseline, threshold)
        baseline_path = Path(baseline)
        compare_path = Path(compare)
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        baseline_images = list(baseline_path.glob("*.png")) + list(baseline_path.glob("*.jpg"))

        console.print(f"[cyan]Comparing {len(baseline_images)} baseline image(s)...[/cyan]")

        for baseline_img in baseline_images:
            current_img = compare_path / baseline_img.name
            if current_img.exists():
                result = comparator.compare(baseline_img, current_img, output_path)

                if result.has_diff:
                    console.print(f"[yellow]⚠[/yellow] {baseline_img.name}: {result.diff_percentage:.1%} diff")
                else:
                    console.print(f"[green]✓[/green] {baseline_img.name}: No visual diff")

    except ImportError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Make sure visual_comparator.py is available[/yellow]")


@cli.command()
@click.option("--url", "-u", required=True, help="URL to audit")
@click.option("--standard", "-s", default="WCAG2AA", help="Accessibility standard")
@click.option("--rules", "-r", multiple=True, help="Specific rules to check")
@click.option("--output", "-o", default="a11y-report.html", help="Output file")
def a11y(url: str, standard: str, rules: tuple, output: str, **kwargs) -> None:
    """Run accessibility audit."""
    console.print(Panel.fit(f"[cyan]Accessibility Audit: {url}[/cyan]", border_style="cyan"))

    try:
        from playwright.sync_api import sync_playwright
        from .a11y_auditor import A11yAuditor

        auditor = A11yAuditor(standard=standard)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            console.print("[cyan]Navigating to URL...[/cyan]")
            page.goto(url, wait_until="networkidle")

            console.print("[cyan]Running accessibility audit...[/cyan]")
            results = auditor.audit(page, rules=list(rules) if rules else None)

            # Print violations
            if results.violations:
                console.print(f"\n[red]Found {len(results.violations)} violation(s):[/red]\n")

                table = Table()
                table.add_column("Rule", style="cyan")
                table.add_column("Severity", style="bold")
                table.add_column("Description")

                for v in results.violations:
                    severity_map = {"critical": "red", "serious": "yellow", "moderate": "yellow", "minor": "green"}
                    table.add_row(
                        v.rule_id,
                        f"[{severity_map.get(v.severity, 'white')}]{v.severity}[/{severity_map.get(v.severity, 'white')}]",
                        v.description[:80],
                    )

                console.print(table)

                # Save report
                auditor.save_report(results, format="html", output=output)
                console.print(f"\n[cyan]Report saved to {output}[/cyan]")
            else:
                console.print("\n[green]✓ No accessibility violations found![/green]")

            browser.close()

    except ImportError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("--url", "-u", required=True, help="URL to test")
@click.option("--actions", "-a", default="click,fill,select", help="Actions to test")
def interact(url: str, actions: str) -> None:
    """Run UI interaction tests."""
    console.print(Panel.fit(f"[cyan]Interaction Testing: {url}[/cyan]", border_style="cyan"))

    try:
        from .interaction_validator import InteractionValidator

        validator = InteractionValidator()
        action_list = [a.strip() for a in actions.split(",")]

        console.print(f"[cyan]Testing actions: {', '.join(action_list)}[/cyan]")

        result = validator.validate(url, action_list)

        if result["success"]:
            console.print("\n[green]✓ All interactions successful![/green]")
        else:
            console.print(f"\n[red]✗ Interaction test failed: {result.get('error')}[/red]")

    except ImportError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("--format", "-f", default="html", type=click.Choice(["html", "json", "markdown"]))
@click.option("--output", "-o", default="./reports", help="Output directory")
@click.option("--input", "-i", default=None, help="Input results file (JSON)")
def report(format: str, output: str, input: str) -> None:
    """Generate test report from results."""
    console.print(Panel.fit(f"[cyan]Generating {format.upper()} report[/cyan]", border_style="cyan"))

    runner = BrowserTestRunner()

    if input:
        results_path = Path(input)
        if results_path.exists():
            runner.results = json.loads(results_path.read_text())
        else:
            console.print(f"[red]Results file not found: {input}[/red]")
            return

    runner.generate_report(output, format)


if __name__ == "__main__":
    cli()
