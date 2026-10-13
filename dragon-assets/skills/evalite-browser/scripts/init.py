#!/usr/bin/env python3
"""
evalite-browser Project Initialization Script

Initializes a new browser testing project with:
- Directory structure
- Default configuration
- Sample test cases
- Baseline screenshots directory
"""

import os
import shutil
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()

DEFAULT_CONFIG = """# evalite-browser Project Configuration
name: "my-browser-tests"
version: "1.0.0"

browser:
  provider: "playwright"
  headless: true
  viewport:
    width: 1280
    height: 720
  browsers:
    - chromium
    - firefox

visual:
  enabled: true
  baseline_dir: "./baseline"
  threshold: 0.1
  diff_highlight: true
  report_format: "html"

a11y:
  enabled: true
  standard: "WCAG2AA"
  rules:
    - color-contrast
    - image-alt
    - label
    - button-name
    - link-name
  report_format: "html"

interaction:
  enabled: true
  wait_for_selectors:
    timeout: 5000
  retry_attempts: 3
  retry_delay: 1000

reporting:
  formats:
    - "html"
    - "json"
    - "markdown"
  output_dir: "./reports"
  include_screenshots: true
  include_console_errors: true
"""

SAMPLE_TEST_CASE = """{
  "name": "example-chat-test",
  "url": "http://localhost:3000/chat",
  "steps": [
    {
      "action": "click",
      "selector": "[data-testid='chat-input']"
    },
    {
      "action": "fill",
      "selector": "[data-testid='chat-input']",
      "value": "Hello, LLM!"
    },
    {
      "action": "click",
      "selector": "[data-testid='send-button']"
    },
    {
      "action": "wait_for_selector",
      "selector": "[data-testid='response']",
      "timeout": 30000
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": "[data-testid='response']"
    },
    {
      "type": "contains_text",
      "selector": "[data-testid='response']",
      "text": "Hello"
    }
  ],
  "visual": {
    "enabled": true,
    "name": "chat-response-visible"
  },
  "a11y": {
    "enabled": true,
    "rules": ["color-contrast", "label"]
  }
}
"""


def create_directory_structure(project_dir: Path) -> None:
    """Create the directory structure for a new project."""
    directories = [
        "tests",
        "baseline",
        "current",
        "reports",
        "reports/diffs",
        "reports/screenshots",
        "configs",
        "logs",
    ]

    for directory in directories:
        dir_path = project_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]+[/green] {directory}/")

    console.print()


def create_config_file(project_dir: Path, config_content: str) -> None:
    """Create the default configuration file."""
    config_path = project_dir / "configs" / "evalite-browser.yaml"
    config_path.write_text(config_content)
    console.print(f"[green]+[/green] {config_path}")


def create_sample_test(project_dir: Path, test_content: str) -> None:
    """Create a sample test case file."""
    test_path = project_dir / "tests" / "example.json"
    test_path.write_text(test_content)
    console.print(f"[green]+[/green] {test_path}")


def create_gitignore(project_dir: Path) -> None:
    """Create a .gitignore file."""
    gitignore_content = """# evalite-browser
__pycache__/
*.pyc
.pytest_cache/

# Playwright
.playwright/
playwright-report/
test-results/

# Screenshots
baseline/
current/
reports/
!baseline/.gitkeep
!current/.gitkeep
!reports/.gitkeep

# Logs
logs/
*.log

# Python
.venv/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    gitignore_path = project_dir / ".gitignore"
    gitignore_path.write_text(gitignore_content)
    console.print(f"[green]+[/green] .gitignore")


def create_gitkeep(base_dir: Path, subdir: str) -> None:
    """Create .gitkeep to preserve empty directories."""
    gitkeep_path = base_dir / subdir / ".gitkeep"
    gitkeep_path.touch()


def check_playwright_installed() -> bool:
    """Check if Playwright is installed."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def install_playwright_browsers() -> None:
    """Install Playwright browsers."""
    import subprocess

    console.print("\n[yellow]Installing Playwright browsers...[/yellow]")

    browsers = ["chromium", "firefox"]
    for browser in browsers:
        console.print(f"  Installing {browser}...")
        try:
            subprocess.run(
                ["playwright", "install", browser],
                check=True,
                capture_output=True,
            )
            console.print(f"  [green]✓[/green] {browser} installed")
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] {browser}: {e}")


@click.command()
@click.option(
    "--name",
    "-n",
    default="my-browser-tests",
    help="Project name",
)
@click.option(
    "--dir",
    "-d",
    default=None,
    help="Project directory (default: current directory)",
)
@click.option(
    "--install-browsers/--no-install-browsers",
    default=True,
    help="Install Playwright browsers",
)
def init(name: str, dir: str, install_browsers: bool) -> None:
    """Initialize a new evalite-browser project."""
    console.print(
        Panel.fit(
            "[bold cyan]evalite-browser[/bold cyan] Project Initialization",
            border_style="cyan",
        )
    )

    # Determine project directory
    if dir:
        project_dir = Path(dir).resolve()
    else:
        project_dir = Path.cwd() / name

    # Create project directory if needed
    if not project_dir.exists():
        console.print(f"\n[yellow]Creating project directory: {project_dir}[/yellow]")
        project_dir.mkdir(parents=True)

    console.print(f"\n[bold]Creating project structure:[/bold]")
    create_directory_structure(project_dir)

    console.print(f"\n[bold]Creating configuration files:[/bold]")
    create_config_file(project_dir, DEFAULT_CONFIG)
    create_sample_test(project_dir, SAMPLE_TEST_CASE)
    create_gitignore(project_dir)

    # Preserve empty directories
    for subdir in ["baseline", "current", "reports"]:
        create_gitkeep(project_dir, subdir)

    # Install Playwright browsers
    if install_browsers:
        if not check_playwright_installed():
            console.print("\n[yellow]Playwright not installed. Installing...[/yellow]")
            try:
                import subprocess
                subprocess.run(
                    ["pip", "install", "playwright"],
                    check=True,
                    capture_output=True,
                )
            except Exception as e:
                console.print(f"[red]Failed to install Playwright: {e}[/red]")
                return

        install_playwright_browsers()

    console.print()
    console.print(
        Panel.fit(
            "[bold green]✓ Project initialized successfully![/bold green]\n\n"
            "Next steps:\n"
            "  1. Edit configs/evalite-browser.yaml with your settings\n"
            "  2. Add your test cases to tests/\n"
            "  3. Run: python scripts/browser_runner.py run --url http://localhost:3000",
            border_style="green",
        )
    )


if __name__ == "__main__":
    init()
