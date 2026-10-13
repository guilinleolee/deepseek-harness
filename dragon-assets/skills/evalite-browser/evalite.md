# evalite-browser Design Reference

> Design patterns, architecture decisions, and implementation guidelines for evalite-browser.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        evalite-browser Architecture                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │   visual_   │    │    a11y_    │    │ interaction_ │           │
│  │ comparator  │    │  auditor    │    │  validator   │           │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘           │
│         │                    │                    │                   │
│         ▼                    ▼                    ▼                   │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                   Browser Runner                          │       │
│  │         (Playwright Multi-Browser Orchestration)          │       │
│  └──────────────────────────┬──────────────────────────────┘       │
│                             │                                        │
│                             ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                   Report Generator                       │       │
│  │         (HTML / JSON / Markdown / SARIF)              │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Zero-Config Defaults

Every module works out-of-the-box with sensible defaults:

```python
# VisualComparator
comparator = VisualComparator(
    baseline_dir="./baseline",
    threshold=0.1,      # 10% diff threshold
    diff_highlight=True,
)

# A11yAuditor
auditor = A11yAuditor(
    standard="WCAG2AA",
    browser="chromium",
    headless=True,
)

# InteractionValidator
validator = InteractionValidator(
    wait_timeout=5000,
    retry_attempts=3,
    retry_delay=1000,
)
```

### 2. Programmatic + CLI Dual Interface

Every module exposes both:

```python
# Programmatic API
result = comparator.compare("screenshot.png")
report = auditor.audit(page)
validation = validator.validate(page, steps, assertions)

# CLI Interface
$ evalite-browser visual compare --baseline ./baseline --compare ./current
$ evalite-browser a11y audit --url https://example.com
$ evalite-browser interaction validate --url https://example.com --steps steps.json
```

### 3. Structured Result Types

All modules return dataclass-based results for programmatic consumption:

```python
@dataclass
class VisualDiffResult:
    baseline_path: str
    current_path: str
    diff_path: Optional[str]
    has_diff: bool
    diff_percentage: float
    diff_regions: List[Dict]

@dataclass
class A11yReport:
    url: str
    violations: List[A11yViolation]
    timestamp: str
    page_title: str

@dataclass
class ValidationResult:
    name: str
    url: str
    steps: List[InteractionStep]
    assertions: List[Assertion]
    step_results: List[InteractionResult]
    assertion_results: List[Dict]
    passed: bool
    duration_ms: float
```

## File Naming Conventions

```
scripts/
├── __init__.py           # Package marker
├── init.py                # Project initialization
├── browser_runner.py      # Main orchestrator (snake_case)
├── visual_comparator.py   # Visual testing module
├── a11y_auditor.py       # Accessibility testing
├── interaction_validator.py # UI interaction testing
└── report_generator.py    # Report generation
```

## CLI Command Structure

```
evalite-browser
├── visual
│   ├── compare           # Compare baseline vs current
│   └── diff              # Generate diff image
├── a11y
│   ├── audit             # Full page audit
│   └── audit-element     # Single element audit
├── interaction
│   └── validate         # Run interaction steps
├── init                  # Initialize project
├── run                   # Run all tests
└── report               # Generate combined report
```

## Result Format Schema

### Visual Diff Result

```json
{
  "baseline_path": "baseline/screenshot.png",
  "current_path": "current/screenshot.png",
  "diff_path": "reports/diffs/diff_screenshot.png",
  "has_diff": true,
  "diff_percentage": 2.5,
  "diff_regions": [
    {
      "x": 100,
      "y": 200,
      "width": 150,
      "height": 50,
      "pixel_count": 7500
    }
  ],
  "threshold": 0.1,
  "timestamp": "2026-05-07T12:00:00"
}
```

### A11y Report

```json
{
  "url": "https://example.com",
  "page_title": "Example Page",
  "page_url": "https://example.com",
  "violations": [
    {
      "id": "color-contrast",
      "impact": "serious",
      "description": "Elements must have sufficient color contrast",
      "help": "https://dequeuniversity.com/rules/axe/4.8/color-contrast",
      "nodes": [
        {
          "html": "<div class='low-contrast'>...</div>",
          "target": [".low-contrast"],
          "impact": "serious"
        }
      ]
    }
  ],
  "timestamp": "2026-05-07T12:00:00",
  "summary": {
    "total": 5,
    "critical": 0,
    "serious": 2,
    "moderate": 1,
    "minor": 2
  }
}
```

### Validation Result

```json
{
  "name": "chat-interaction-test",
  "url": "https://example.com/chat",
  "steps": [
    {"action": "click", "selector": "#input"},
    {"action": "fill", "selector": "#input", "value": "Hello"}
  ],
  "assertions": [
    {"type": "visible", "selector": "#response"}
  ],
  "step_results": [
    {"action": "click", "selector": "#input", "success": true, "duration_ms": 150}
  ],
  "assertion_results": [
    {"type": "visible", "selector": "#response", "passed": true}
  ],
  "passed": true,
  "duration_ms": 1250,
  "timestamp": "2026-05-07T12:00:00"
}
```

## Error Handling Patterns

### Retry with Backoff

```python
def _execute_step(self, page, step, step_index):
    last_error = None
    for attempt in range(self.retry_attempts):
        try:
            self._handle_action(page, step)
            return InteractionResult(success=True, ...)
        except Exception as e:
            last_error = str(e)
            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay / 1000 * (attempt + 1))  # Linear backoff
    return InteractionResult(success=False, error=last_error)
```

### Graceful Degradation

```python
def audit(self, page, url=None):
    try:
        self._inject_axe(page)
        results = page.evaluate("""async () => {
            const { default: axe } = await import('/node_modules/axe-core/axe.min.js');
            return await axe.run();
        }""")
    except Exception as e:
        # Fallback: manual checks if axe fails
        return self._manual_a11y_check(page)
```

## Threshold Calibration

### Visual Diff Thresholds

| Use Case | Threshold | Rationale |
|----------|-----------|-----------|
| Pixel-perfect UI | 0.0-0.01 | No visual drift allowed |
| Content-heavy pages | 0.05-0.1 | Dynamic content may cause noise |
| Charts/Graphs | 0.1-0.2 | Anti-aliasing varies by renderer |
| Screenshots with timestamps | 0.5+ | Ignore time-dependent elements |

### A11y Impact Levels

| Level | WCAG Violation | User Impact |
|-------|---------------|------------|
| Critical | Must-fix | Content inaccessible |
| Serious | Should-fix | Significant barriers |
| Moderate | Should-fix | Minor barriers |
| Minor | May-fix | Minimal impact |

## Browser Compatibility Matrix

| Feature | Chromium | Firefox | WebKit |
|---------|-----------|---------|--------|
| Screenshots | Full | Full | Full |
| A11y Audit | Full | Full | Partial |
| Interactions | Full | Full | Full |
| Console Capture | Full | Full | Limited |

## Performance Benchmarks

| Operation | Target | Max |
|-----------|--------|-----|
| Page Load | 1s | 5s |
| Screenshot Capture | 100ms | 500ms |
| Visual Diff | 500ms | 2s |
| A11y Audit | 2s | 10s |
| Interaction Step | 200ms | 1s |
| Full Test Suite | 30s | 120s |

## Integration Patterns

### With eval-harness

```python
from eval_harness import TestSuite

suite = TestSuite("llm-app-e2e")
suite.add_test("visual", lambda: comparator.compare("chat.png"))
suite.add_test("a11y", lambda: auditor.audit(page))
suite.add_test("interaction", lambda: validator.validate(page, steps, assertions))
results = suite.run()
```

### With CI/CD

```yaml
# GitHub Actions
- name: Run evalite-browser
  run: |
    python -m evalite_browser run \
      --url ${{ env.APP_URL }} \
      --baseline ./baseline \
      --report ./reports/results.json
  env:
    PLAYWRIGHT_BROWSERS_PATH: .playwright
```

## Anti-Patterns to Avoid

1. **Screenshot Timestamp Dependence** - Always use `datetime` normalization or element-specific screenshots
2. **Hardcoded Timeouts** - Use configuration or adaptive timeouts based on network conditions
3. **Global State** - Each module should be stateless and thread-safe
4. **Monolithic Reports** - Generate per-test reports for parallel execution
5. **Ignoring A11y Violations** - Even "minor" violations compound into inaccessible experiences
