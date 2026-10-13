#!/usr/bin/env python3
"""
evalite-browser Interaction Validator

UI interaction testing module for validating user interactions
like clicks, fills, selections, hovers, and drags.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class ActionType(Enum):
    """Supported interaction action types."""
    CLICK = "click"
    DOUBLE_CLICK = "dblclick"
    RIGHT_CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    HOVER = "hover"
    DRAG = "drag"
    SCROLL = "scroll"
    PRESS = "press"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_TIMEOUT = "wait_for_timeout"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"


@dataclass
class InteractionStep:
    """Single interaction step in a test."""
    action: str
    selector: Optional[str] = None
    value: Optional[Any] = None
    timeout: int = 5000
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.action = self.action.lower()


@dataclass
class Assertion:
    """Assertion to verify after interactions."""
    type: str  # visible, hidden, contains_text, has_value, has_attribute, etc.
    selector: Optional[str] = None
    value: Optional[Any] = None
    expected: Optional[Any] = None

    def __post_init__(self):
        self.type = self.type.lower()


@dataclass
class InteractionResult:
    """Result of a single interaction."""
    action: str
    selector: Optional[str]
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0
    screenshot: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationResult:
    """Result of interaction validation test."""
    name: str
    url: str
    steps: List[InteractionStep]
    assertions: List[Assertion]
    step_results: List[InteractionResult] = field(default_factory=list)
    assertion_results: List[Dict[str, Any]] = field(default_factory=list)
    passed: bool = False
    duration_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "url": self.url,
            "steps": [vars(s) for s in self.steps],
            "assertions": [vars(a) for a in self.assertions],
            "step_results": [vars(r) for r in self.step_results],
            "assertion_results": self.assertion_results,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


class InteractionValidator:
    """
    UI interaction validator for browser testing.

    Supports clicks, fills, selects, hovers, drags, and various assertions.
    """

    def __init__(
        self,
        wait_timeout: int = 5000,
        retry_attempts: int = 3,
        retry_delay: int = 1000,
        screenshot_on_error: bool = True,
    ):
        self.wait_timeout = wait_timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.screenshot_on_error = screenshot_on_error
        self._page = None
        self._context = None

    def validate(
        self,
        page,
        steps: List[InteractionStep],
        assertions: List[Assertion],
        test_name: str = "interaction_test",
        url: str = "",
        screenshot_dir: str = "./reports/screenshots",
    ) -> ValidationResult:
        """
        Validate interactions on a page.

        Args:
            page: Playwright page object
            steps: List of interaction steps
            assertions: List of assertions to verify
            test_name: Name of the test
            url: URL being tested
            screenshot_dir: Directory for error screenshots

        Returns:
            ValidationResult with step and assertion results
        """
        self._page = page
        self._screenshot_dir = Path(screenshot_dir)
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        result = ValidationResult(
            name=test_name,
            url=url or (page.url if page else ""),
            steps=steps,
            assertions=assertions,
        )

        # Execute steps
        for i, step in enumerate(steps):
            step_result = self._execute_step(page, step, i)
            result.step_results.append(step_result)

            if not step_result.success:
                # Take screenshot on failure
                if self.screenshot_on_error:
                    screenshot_path = self._screenshot_dir / f"{test_name}_step_{i}.png"
                    page.screenshot(path=str(screenshot_path))
                    step_result.screenshot = str(screenshot_path)

                # Stop on first failure unless it's a wait step
                if step.action not in ["wait_for_selector", "wait_for_timeout", "wait_for_navigation"]:
                    break

        # Execute assertions
        for assertion in assertions:
            assertion_result = self._execute_assertion(page, assertion)
            result.assertion_results.append(assertion_result)

        result.duration_ms = (time.time() - start_time) * 1000
        result.passed = all(r.success for r in result.step_results) and \
                       all(r["passed"] for r in result.assertion_results)

        return result

    def _execute_step(
        self,
        page,
        step: InteractionStep,
        step_index: int,
    ) -> InteractionResult:
        """Execute a single interaction step with retry logic."""
        start_time = time.time()
        last_error = None

        for attempt in range(self.retry_attempts):
            try:
                if step.action == "click":
                    self._handle_click(page, step)
                elif step.action == "dblclick" or step.action == "double_click":
                    self._handle_double_click(page, step)
                elif step.action == "fill":
                    self._handle_fill(page, step)
                elif step.action == "select":
                    self._handle_select(page, step)
                elif step.action == "check":
                    self._handle_check(page, step, checked=True)
                elif step.action == "uncheck":
                    self._handle_check(page, step, checked=False)
                elif step.action == "hover":
                    self._handle_hover(page, step)
                elif step.action == "drag":
                    self._handle_drag(page, step)
                elif step.action == "scroll":
                    self._handle_scroll(page, step)
                elif step.action == "press":
                    self._handle_press(page, step)
                elif step.action == "wait_for_selector":
                    self._handle_wait_for_selector(page, step)
                elif step.action == "wait_for_timeout":
                    self._handle_wait_for_timeout(step)
                elif step.action == "wait_for_navigation":
                    self._handle_wait_for_navigation(page, step)
                elif step.action == "screenshot":
                    self._handle_screenshot(page, step, step_index)
                elif step.action == "evaluate":
                    self._handle_evaluate(page, step)
                else:
                    raise ValueError(f"Unknown action: {step.action}")

                return InteractionResult(
                    action=step.action,
                    selector=step.selector,
                    success=True,
                    duration_ms=(time.time() - start_time) * 1000,
                )

            except Exception as e:
                last_error = str(e)
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay / 1000)

        return InteractionResult(
            action=step.action,
            selector=step.selector,
            success=False,
            error=last_error,
            duration_ms=(time.time() - start_time) * 1000,
        )

    def _handle_click(self, page, step: InteractionStep) -> None:
        """Handle click action."""
        if step.options.get("button") == "right":
            page.click(step.selector, button="right", timeout=step.timeout)
        else:
            page.click(step.selector, timeout=step.timeout)

    def _handle_double_click(self, page, step: InteractionStep) -> None:
        """Handle double click action."""
        page.dblclick(step.selector, timeout=step.timeout)

    def _handle_fill(self, page, step: InteractionStep) -> None:
        """Handle fill action."""
        page.fill(step.selector, step.value, timeout=step.timeout)

    def _handle_select(self, page, step: InteractionStep) -> None:
        """Handle select action."""
        page.select_option(step.selector, step.value, timeout=step.timeout)

    def _handle_check(self, page, step: InteractionStep, checked: bool) -> None:
        """Handle check/uncheck action."""
        is_checked = page.is_checked(step.selector)
        if (checked and not is_checked) or (not checked and is_checked):
            page.check(step.selector, timeout=step.timeout) if checked else \
                page.uncheck(step.selector, timeout=step.timeout)

    def _handle_hover(self, page, step: InteractionStep) -> None:
        """Handle hover action."""
        page.hover(step.selector, timeout=step.timeout)

    def _handle_drag(self, page, step: InteractionStep) -> None:
        """Handle drag action."""
        source = step.selector
        target = step.options.get("target", "")
        page.drag_and_drop(source, target, timeout=step.timeout)

    def _handle_scroll(self, page, step: InteractionStep) -> None:
        """Handle scroll action."""
        if step.selector:
            page.evaluate(
                f"""
                () => {{
                    const el = document.querySelector('{step.selector}');
                    if (el) el.scrollTop += {step.value or 500};
                    else window.scrollBy(0, {step.value or 500});
                }}
                """
            )
        else:
            page.evaluate(f"window.scrollBy(0, {step.value or 500})")

    def _handle_press(self, page, step: InteractionStep) -> None:
        """Handle keyboard press action."""
        if step.selector:
            page.press(step.selector, step.value, timeout=step.timeout)
        else:
            page.keyboard.press(step.value)

    def _handle_wait_for_selector(
        self, page, step: InteractionStep
    ) -> None:
        """Handle wait for selector action."""
        state = step.options.get("state", "visible")
        page.wait_for_selector(
            step.selector,
            state=state,
            timeout=step.timeout,
        )

    def _handle_wait_for_timeout(self, step: InteractionStep) -> None:
        """Handle wait for timeout action."""
        time.sleep(step.timeout / 1000)

    def _handle_wait_for_navigation(self, page, step: InteractionStep) -> None:
        """Handle wait for navigation action."""
        url = step.options.get("url")
        if url:
            page.wait_for_url(url, timeout=step.timeout)
        else:
            page.wait_for_load_state("networkidle", timeout=step.timeout)

    def _handle_screenshot(
        self, page, step: InteractionStep, step_index: int
    ) -> None:
        """Handle screenshot action."""
        name = step.options.get("name", f"step_{step_index}")
        path = self._screenshot_dir / f"{name}.png"
        page.screenshot(path=str(path))

    def _handle_evaluate(self, page, step: InteractionStep) -> None:
        """Handle evaluate action."""
        page.evaluate(step.value)

    def _execute_assertion(
        self, page, assertion: Assertion
    ) -> Dict[str, Any]:
        """Execute an assertion."""
        try:
            if assertion.type == "visible":
                return self._assert_visible(page, assertion)
            elif assertion.type == "hidden":
                return self._assert_hidden(page, assertion)
            elif assertion.type == "contains_text":
                return self._assert_contains_text(page, assertion)
            elif assertion.type == "has_value":
                return self._assert_has_value(page, assertion)
            elif assertion.type == "has_attribute":
                return self._assert_has_attribute(page, assertion)
            elif assertion.type == "has_count":
                return self._assert_has_count(page, assertion)
            elif assertion.type == "enabled":
                return self._assert_enabled(page, assertion)
            elif assertion.type == "disabled":
                return self._assert_disabled(page, assertion)
            elif assertion.type == "checked":
                return self._assert_checked(page, assertion)
            elif assertion.type == "url_matches":
                return self._assert_url_matches(page, assertion)
            elif assertion.type == "title_matches":
                return self._assert_title_matches(page, assertion)
            else:
                return {
                    "passed": False,
                    "error": f"Unknown assertion type: {assertion.type}",
                }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _assert_visible(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element is visible."""
        if assertion.selector:
            is_visible = page.is_visible(assertion.selector)
        else:
            return {"passed": True, "type": "visible"}
        return {"passed": is_visible, "type": "visible", "selector": assertion.selector}

    def _assert_hidden(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element is hidden."""
        is_hidden = not page.is_visible(assertion.selector)
        return {"passed": is_hidden, "type": "hidden", "selector": assertion.selector}

    def _assert_contains_text(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element contains text."""
        if not assertion.selector:
            return {"passed": False, "error": "Selector required for contains_text"}

        text = page.text_content(assertion.selector)
        contains = assertion.expected in text if text else False
        return {
            "passed": contains,
            "type": "contains_text",
            "selector": assertion.selector,
            "expected": assertion.expected,
            "actual": text[:100] if text else "",
        }

    def _assert_has_value(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert input has specific value."""
        if not assertion.selector:
            return {"passed": False, "error": "Selector required for has_value"}

        value = page.input_value(assertion.selector)
        return {
            "passed": assertion.expected == value,
            "type": "has_value",
            "selector": assertion.selector,
            "expected": assertion.expected,
            "actual": value,
        }

    def _assert_has_attribute(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element has attribute with value."""
        if not assertion.selector:
            return {"passed": False, "error": "Selector required for has_attribute"}

        actual = page.get_attribute(assertion.selector, assertion.value)
        return {
            "passed": assertion.expected == actual,
            "type": "has_attribute",
            "selector": assertion.selector,
            "attribute": assertion.value,
            "expected": assertion.expected,
            "actual": actual,
        }

    def _assert_has_count(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert number of matching elements."""
        count = len(page.query_selector_all(assertion.selector))
        return {
            "passed": assertion.expected == count,
            "type": "has_count",
            "selector": assertion.selector,
            "expected": assertion.expected,
            "actual": count,
        }

    def _assert_enabled(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element is enabled."""
        is_enabled = not page.is_disabled(assertion.selector)
        return {"passed": is_enabled, "type": "enabled", "selector": assertion.selector}

    def _assert_disabled(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert element is disabled."""
        is_disabled = page.is_disabled(assertion.selector)
        return {"passed": is_disabled, "type": "disabled", "selector": assertion.selector}

    def _assert_checked(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert checkbox is checked."""
        is_checked = page.is_checked(assertion.selector)
        return {"passed": is_checked, "type": "checked", "selector": assertion.selector}

    def _assert_url_matches(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert URL matches pattern."""
        import re
        actual = page.url
        pattern = assertion.expected
        matches = bool(re.match(pattern, actual)) if pattern else True
        return {
            "passed": matches,
            "type": "url_matches",
            "expected": pattern,
            "actual": actual,
        }

    def _assert_title_matches(self, page, assertion: Assertion) -> Dict[str, Any]:
        """Assert page title matches pattern."""
        import re
        actual = page.title()
        pattern = assertion.expected
        matches = bool(re.search(pattern, actual)) if pattern else True
        return {
            "passed": matches,
            "type": "title_matches",
            "expected": pattern,
            "actual": actual,
        }


# CLI Commands
@click.group()
def cli():
    """Interaction validation CLI."""
    pass


@cli.command()
@click.option("--url", "-u", required=True, help="URL to test")
@click.option("--steps", "-s", type=click.Path(exists=True), help="JSON file with steps")
@click.option("--output", "-o", default="interaction-results.json", help="Output file")
def validate(url: str, steps: str, output: str):
    """Validate interactions on a page."""
    try:
        from playwright.sync_api import sync_playwright

        # Load steps from file or use defaults
        if steps:
            with open(steps) as f:
                data = json.load(f)
                step_list = [InteractionStep(**s) for s in data.get("steps", [])]
                assertion_list = [Assertion(**a) for a in data.get("assertions", [])]
                test_name = data.get("name", "interaction_test")
        else:
            step_list = []
            assertion_list = []
            test_name = "interaction_test"

        validator = InteractionValidator()

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            console.print(f"[cyan]Navigating to: {url}[/cyan]")
            page.goto(url, wait_until="networkidle")

            result = validator.validate(
                page=page,
                steps=step_list,
                assertions=assertion_list,
                test_name=test_name,
                url=url,
            )

            # Save results
            with open(output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)

            # Print summary
            _print_validation_result(result)

            browser.close()

    except ImportError:
        console.print("[red]Playwright not installed.[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def _print_validation_result(result: ValidationResult):
    """Print validation result to console."""
    status = "[green]PASSED[/green]" if result.passed else "[red]FAILED[/red]"

    console.print(Panel.fit(
        f"[bold]{result.name}[/bold]\n"
        f"Status: {status}\n"
        f"Duration: {result.duration_ms:.0f}ms\n"
        f"Steps: {sum(1 for s in result.step_results if s.success)}/{len(result.step_results)} passed",
        title="Interaction Validation",
        border_style="green" if result.passed else "red",
    ))

    # Step results
    if result.step_results:
        table = Table(title="Step Results")
        table.add_column("Step", style="cyan")
        table.add_column("Action", style="white")
        table.add_column("Selector", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="dim")

        for i, step_result in enumerate(result.step_results):
            status_text = "[green]OK[/green]" if step_result.success else "[red]FAIL[/red]"
            table.add_row(
                str(i + 1),
                step_result.action,
                step_result.selector or "-",
                status_text,
                f"{step_result.duration_ms:.0f}ms",
            )

        console.print(table)

    # Assertion results
    if result.assertion_results:
        table = Table(title="Assertion Results")
        table.add_column("Type", style="cyan")
        table.add_column("Selector", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        for assertion_result in result.assertion_results:
            status_text = "[green]PASS[/green]" if assertion_result["passed"] else "[red]FAIL[/red]"
            details = assertion_result.get("error", "")
            if "expected" in assertion_result:
                details = f"Expected: {assertion_result['expected']}, Actual: {assertion_result.get('actual', 'N/A')}"
            table.add_row(
                assertion_result.get("type", ""),
                assertion_result.get("selector", "-"),
                status_text,
                details[:50],
            )

        console.print(table)


if __name__ == "__main__":
    cli()
