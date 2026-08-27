#!/usr/bin/env python3
"""
evalite-browser A11y Auditor

WCAG 2.1 AA accessibility compliance auditing module.
Provides automated accessibility testing using axe-core rules.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()


@dataclass
class A11yViolation:
    """Represents an accessibility violation."""
    id: str
    impact: str  # critical, serious, moderate, minor
    description: str
    help: str
    help_url: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "impact": self.impact,
            "description": self.description,
            "help": self.help,
            "help_url": self.help_url,
            "nodes": self.nodes,
            "count": self.count,
        }


@dataclass
class A11yReport:
    """Accessibility audit report."""
    url: str
    violations: List[A11yViolation] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    page_title: str = ""
    page_url: str = ""

    @property
    def total_violations(self) -> int:
        return len(self.violations)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.impact == "critical")

    @property
    def serious_count(self) -> int:
        return sum(1 for v in self.violations if v.impact == "serious")

    @property
    def moderate_count(self) -> int:
        return sum(1 for v in self.violations if v.impact == "moderate")

    @property
    def minor_count(self) -> int:
        return sum(1 for v in self.violations if v.impact == "minor")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "page_title": self.page_title,
            "page_url": self.page_url,
            "violations": [v.to_dict() for v in self.violations],
            "timestamp": self.timestamp,
            "summary": {
                "total": self.total_violations,
                "critical": self.critical_count,
                "serious": self.serious_count,
                "moderate": self.moderate_count,
                "minor": self.minor_count,
            },
        }


# Default WCAG 2.1 AA rules
DEFAULT_RULES = [
    "color-contrast",
    "image-alt",
    "label",
    "button-name",
    "link-name",
    "aria-required-attr",
    "aria-valid-attr",
    "aria-valid-attr-value",
    "duplicate-id",
    "heading-order",
    "region",
    "skip-link",
    "tab-index",
    "aria-hidden-body",
    "empty-heading",
    "button-has-visible-text",
    "document-title",
    "html-has-lang",
    "html-lang-valid",
]

# Impact colors
IMPACT_COLORS = {
    "critical": "red",
    "serious": "yellow",
    "moderate": "blue",
    "minor": "cyan",
}


class A11yAuditor:
    """
    Accessibility auditor for WCAG 2.1 AA compliance.

    Uses Playwright and axe-core for automated accessibility testing.
    """

    def __init__(
        self,
        standard: str = "WCAG2AA",
        rules: Optional[List[str]] = None,
        browser: str = "chromium",
        headless: bool = True,
    ):
        self.standard = standard
        self.rules = rules or DEFAULT_RULES
        self.browser = browser
        self.headless = headless
        self._playwright = None
        self._browser = None

    def audit(self, page, url: Optional[str] = None) -> A11yReport:
        """
        Run accessibility audit on a page.

        Args:
            page: Playwright page object or URL string
            url: URL to audit (if page is None)

        Returns:
            A11yReport with violations
        """
        # Handle both Playwright page and URL
        if isinstance(page, str):
            url = page
            page = None

        if page is None and url:
            page = self._get_page(url)

        if page is None:
            raise ValueError("Either page or url must be provided")

        # Inject axe-core
        self._inject_axe(page)

        # Run axe audit
        results = page.evaluate("""
            async () => {
                const { default: axe } = await import('/node_modules/axe-core/axe.min.js');
                return await axe.run();
            }
        """)

        # Parse results
        report = A11yReport(
            url=url or page.url,
            page_title=page.title(),
            page_url=page.url,
        )

        for violation in results.get("violations", []):
            nodes = []
            for node in violation.get("nodes", []):
                nodes.append({
                    "html": node.get("html", ""),
                    "target": node.get("target", []),
                    "impact": node.get("impact", ""),
                })

            report.violations.append(A11yViolation(
                id=violation.get("id", ""),
                impact=violation.get("impact", ""),
                description=violation.get("description", ""),
                help=violation.get("help", ""),
                help_url=violation.get("helpUrl", ""),
                nodes=nodes,
            ))

        return report

    def audit_element(self, page, selector: str) -> A11yReport:
        """Audit a specific element."""
        # Inject axe-core
        self._inject_axe(page)

        # Run axe on specific element
        results = page.evaluate(f"""
            async () => {{
                const element = document.querySelector('{selector}');
                if (!element) return {{ violations: [] }};
                const {{ default: axe }} = await import('/node_modules/axe-core/axe.min.js');
                return await axe.run(element);
            }}
        """)

        report = A11yReport(
            url=page.url,
            page_title=page.title(),
            page_url=page.url,
        )

        for violation in results.get("violations", []):
            nodes = []
            for node in violation.get("nodes", []):
                nodes.append({
                    "html": node.get("html", ""),
                    "target": node.get("target", []),
                    "impact": node.get("impact", ""),
                })

            report.violations.append(A11yViolation(
                id=violation.get("id", ""),
                impact=violation.get("impact", ""),
                description=violation.get("description", ""),
                help=violation.get("help", ""),
                help_url=violation.get("helpUrl", ""),
                nodes=nodes,
            ))

        return report

    def _inject_axe(self, page) -> None:
        """Inject axe-core into the page."""
        # Check if axe is already loaded
        is_loaded = page.evaluate("""
            () => typeof window.axe !== 'undefined'
        """)

        if not is_loaded:
            # Inject axe-core via CDN
            page.goto(
                "about:blank",
                wait_until="domcontentloaded",
            )
            page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
            )

    def _get_page(self, url: str):
        """Get a Playwright page for the given URL."""
        try:
            from playwright.sync_api import sync_playwright

            pw = sync_playwright().start()
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="networkidle")

            return page
        except ImportError:
            console.print(
                "[red]Playwright not installed. Run: pip install playwright && playwright install chromium[/red]"
            )
            return None

    def save_report(
        self,
        report: A11yReport,
        format: str = "html",
        output: str = "a11y-report",
    ) -> None:
        """Save audit report to file."""
        if format == "html":
            self._save_html_report(report, output)
        elif format == "json":
            self._save_json_report(report, output)
        elif format == "markdown":
            self._save_markdown_report(report, output)

    def _save_html_report(self, report: A11yReport, output: str) -> None:
        """Save HTML report."""
        timestamp = datetime.now().isoformat()

        violations_html = ""
        for v in report.violations:
            color = IMPACT_COLORS.get(v.impact, "gray")
            violations_html += f"""
            <div class="violation {v.impact}">
                <h3>[{v.impact.upper()}] {v.id}</h3>
                <p><strong>Description:</strong> {v.description}</p>
                <p><strong>Help:</strong> <a href="{v.help_url}">{v.help}</a></p>
                <details>
                    <summary>Affected Elements ({len(v.nodes)})</summary>
                    <ul>
            """
            for node in v.nodes[:5]:  # Limit to 5 nodes
                html_snippet = node["html"][:200] + "..." if len(node["html"]) > 200 else node["html"]
                violations_html += f"<li><code>{html_snippet}</code></li>"
            if len(v.nodes) > 5:
                violations_html += f"<li>... and {len(v.nodes) - 5} more</li>"
            violations_html += "</ul></details></div>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>A11y Accessibility Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
        .stat.critical {{ border-left: 4px solid #ef4444; }}
        .stat.serious {{ border-left: 4px solid #f59e0b; }}
        .stat.moderate {{ border-left: 4px solid #3b82f6; }}
        .stat.minor {{ border-left: 4px solid #06b6d4; }}
        .stat .number {{ font-size: 36px; font-weight: bold; }}
        .violation {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 16px; }}
        .violation.critical {{ border-left: 4px solid #ef4444; }}
        .violation.serious {{ border-left: 4px solid #f59e0b; }}
        .violation.moderate {{ border-left: 4px solid #3b82f6; }}
        .violation.minor {{ border-left: 4px solid #06b6d4; }}
        .violation h3 {{ margin-top: 0; color: #374151; }}
        .violation code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }}
        .violation ul {{ max-height: 200px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Accessibility Audit Report</h1>
        <p>URL: <a href="{report.page_url}">{report.page_url}</a></p>
        <p>Title: {report.page_title}</p>
        <p>Generated: {timestamp}</p>
    </div>
    <div class="summary">
        <div class="stat critical">
            <div class="number">{report.critical_count}</div>
            <div>Critical</div>
        </div>
        <div class="stat serious">
            <div class="number">{report.serious_count}</div>
            <div>Serious</div>
        </div>
        <div class="stat moderate">
            <div class="number">{report.moderate_count}</div>
            <div>Moderate</div>
        </div>
        <div class="stat minor">
            <div class="number">{report.minor_count}</div>
            <div>Minor</div>
        </div>
    </div>
    {violations_html or '<p style="background:white;padding:20px;border-radius:8px;">No violations found!</p>'}
</body>
</html>"""

        with open(output if output.endswith(".html") else f"{output}.html", "w", encoding="utf-8") as f:
            f.write(html)

    def _save_json_report(self, report: A11yReport, output: str) -> None:
        """Save JSON report."""
        with open(output if output.endswith(".json") else f"{output}.json", "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

    def _save_markdown_report(self, report: A11yReport, output: str) -> None:
        """Save Markdown report."""
        lines = [
            "# Accessibility Audit Report",
            "",
            f"**URL:** {report.page_url}",
            f"**Title:** {report.page_title}",
            f"**Generated:** {report.timestamp}",
            "",
            "## Summary",
            "",
            f"- Critical: **{report.critical_count}**",
            f"- Serious: **{report.serious_count}**",
            f"- Moderate: **{report.moderate_count}**",
            f"- Minor: **{report.minor_count}**",
            "",
            "## Violations",
            "",
        ]

        for v in report.violations:
            color = IMPACT_COLORS.get(v.impact, "gray")
            lines.append(f"### [{v.impact.upper()}] {v.id}")
            lines.append("")
            lines.append(f"**Description:** {v.description}")
            lines.append("")
            lines.append(f"**Help:** {v.help}")
            lines.append("")
            lines.append(f"**Help URL:** [{v.help_url}]({v.help_url})")
            lines.append("")
            lines.append(f"**Affected Elements:** {len(v.nodes)}")
            lines.append("")

            for node in v.nodes[:3]:
                lines.append(f"```html\n{node['html'][:200]}\n```")

            lines.append("---")
            lines.append("")

        with open(output if output.endswith(".md") else f"{output}.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# CLI Commands
@click.group()
def cli():
    """Accessibility auditing CLI."""
    pass


@cli.command()
@click.option("--url", "-u", required=True, help="URL to audit")
@click.option("--output", "-o", default="a11y-report", help="Output file path")
@click.option("--format", "-f", type=click.Choice(["html", "json", "markdown"]), default="html", help="Report format")
@click.option("--rules", "-r", multiple=True, help="Specific rules to check")
@click.option("--standard", "-s", default="WCAG2AA", help="Accessibility standard")
def audit(url: str, output: str, format: str, rules: tuple, standard: str):
    """Run accessibility audit on a URL."""
    auditor = A11yAuditor(standard=standard, rules=list(rules) if rules else None)

    console.print(f"[cyan]Auditing: {url}[/cyan]")

    # Use Playwright to open page and run audit
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, wait_until="networkidle")

            report = auditor.audit(page)

            # Save report
            auditor.save_report(report, format=format, output=output)

            # Print summary
            _print_summary(report)

            browser.close()

    except ImportError:
        console.print(
            "[red]Playwright not installed. Run: pip install playwright && playwright install chromium[/red]"
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("--url", "-u", required=True, help="URL to audit")
@click.option("--selector", "-s", required=True, help="CSS selector to audit")
@click.option("--output", "-o", default="a11y-element-report", help="Output file path")
def audit_element(url: str, selector: str, output: str):
    """Audit a specific element on a page."""
    auditor = A11yAuditor()

    console.print(f"[cyan]Auditing element '{selector}' on: {url}[/cyan]")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, wait_until="networkidle")

            report = auditor.audit_element(page, selector)

            # Save report
            auditor.save_report(report, format="markdown", output=output)

            # Print summary
            _print_summary(report)

            browser.close()

    except ImportError:
        console.print("[red]Playwright not installed.[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def _print_summary(report: A11yReport):
    """Print audit summary to console."""
    if report.total_violations == 0:
        console.print(Panel.fit(
            "[bold green]No accessibility violations found![/bold green]",
            title="A11y Audit Complete",
            border_style="green",
        ))
        return

    table = Table(title="A11y Violations by Impact")
    table.add_column("Impact", style="cyan")
    table.add_column("Count", style="white")

    counts = {
        "critical": report.critical_count,
        "serious": report.serious_count,
        "moderate": report.moderate_count,
        "minor": report.minor_count,
    }

    for impact, count in counts.items():
        if count > 0:
            color = IMPACT_COLORS.get(impact, "white")
            table.add_row(f"[{color}]{impact.upper()}[/{color}]", str(count))

    console.print(table)

    # Show top violations
    tree = Tree("[bold]Top Violations[/bold]")
    for v in report.violations[:5]:
        color = IMPACT_COLORS.get(v.impact, "white")
        node = tree.add(
            f"[{color}]{v.id}[/{color}] - {len(v.nodes)} element(s)"
        )
        node.add(f"[bold]Help:[/bold] {v.help}")

    console.print(tree)

    console.print(f"\n[bold]Total:[/bold] {report.total_violations} violations")


if __name__ == "__main__":
    cli()
