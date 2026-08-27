---
license: UNKNOWN
triggers: ["evalite browser", "evalite-browser"]
---
# evalite-browser

> Browser-based E2E Testing for LLM Apps — Built on evalite

## L0: 一句话

浏览器端到端测试框架，为 LLM 应用提供 Playwright 驱动的视觉测试、无障碍验证和 UI 交互验证。

## L1: 使用场景

- **视觉回归检测**：捕获截图，对比视觉差异，检测 LLM UI 变化
- **无障碍合规审计**：WCAG 2.1 AA 合规性自动检测
- **UI 交互验证**：验证 LLM 应用的按钮、表单、对话交互
- **跨浏览器测试**：Chrome/Firefox/Safari 多浏览器一致性
- **响应式布局测试**：移动/平板/桌面多视口验证

## L2: 详细文档

### 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                 evalite-browser Architecture                    │
├─────────────────────────────────────────────────────────────┤
│  Playwright Driver          浏览器自动化引擎               │
│         ↓                                                  │
│  Visual Comparator           视觉差异对比                   │
│         ↓                                                  │
│  A11y Auditor              无障碍合规检测                   │
│         ↓                                                  │
│  UI Interaction Validator   UI 交互验证                    │
│         ↓                                                  │
│  Report Generator           测试报告生成                     │
└─────────────────────────────────────────────────────────────┘
```

### 与 evalite-native 的关系

evalite-browser 是 evalite-native 的浏览器扩展，专门针对需要真实浏览器环境的 LLM 应用：

| 维度 | evalite-native | evalite-browser |
|------|---------------|----------------|
| **测试环境** | API/CLI 测试 | 真实浏览器渲染 |
| **适用场景** | 后端逻辑、API 响应 | 前端 UI、视觉呈现 |
| **视觉检测** | 无 | 截图对比 + 差异高亮 |
| **无障碍检测** | 无 | WCAG 2.1 AA 审计 |
| **交互验证** | 有限 | 完整 UI 交互 |

### 安装与配置

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
playwright install firefox
playwright install webkit

# 运行测试
python scripts/browser_runner.py run --url "http://localhost:3000"

# 视觉回归测试
python scripts/browser_runner.py visual --baseline ./baseline --compare ./current

# 无障碍审计
python scripts/browser_runner.py a11y --url "http://localhost:3000" --standard WCAG2AA
```

### 核心命令

```bash
# 初始化项目
python scripts/init.py

# 运行浏览器测试
python scripts/browser_runner.py run --url "http://localhost:3000" --tests ./tests

# 视觉回归检测
python scripts/browser_runner.py visual --baseline ./baseline --compare ./current --threshold 0.1

# 无障碍审计
python scripts/browser_runner.py a11y --url "http://localhost:3000" --standard WCAG2AA --report a11y-report.html

# 交互验证
python scripts/browser_runner.py interact --url "http://localhost:3000" --actions click,fill,select

# 生成报告
python scripts/browser_runner.py report --format html --output ./reports
```

### 配置文件

创建 `configs/evalite-browser.yaml`:

```yaml
name: "my-app-browser-tests"
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
    # - webkit  # 需要 macOS

visual:
  enabled: true
  baseline_dir: "./baseline"
  threshold: 0.1  # 10% 差异阈值
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
```

### 测试用例格式

```json
{
  "name": "chat-input-submission",
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
```

### 视觉对比示例

```python
from evalite_browser.visual import VisualComparator

comparator = VisualComparator(
    baseline_dir="./baseline",
    threshold=0.1,
    diff_highlight=True
)

result = comparator.compare(
    baseline="chat-page.png",
    current="chat-page-2026-05-07.png",
    output_dir="./reports/diffs"
)

if result.has_diff:
    print(f"视觉差异: {result.diff_percentage:.1%}")
    print(f"差异位置: {result.diff_regions}")
    result.save_diff_image("chat-page-diff.png")
```

### 无障碍检测示例

```python
from evalite_browser.a11y import A11yAuditor

auditor = A11yAuditor(standard="WCAG2AA")

results = auditor.audit(
    url="http://localhost:3000/chat",
    rules=["color-contrast", "image-alt", "label", "button-name"]
)

for violation in results.violations:
    print(f"[{violation.severity}] {violation.rule_id}: {violation.description}")
    print(f"  元素: {violation.node}")
    print(f"  建议: {violation.help}")

auditor.save_report(results, format="html", output="a11y-report.html")
```

### 与 LLM 应用集成

evalite-browser 专门针对 LLM 应用设计：

```python
from evalite_browser.runner import LLMAppTester

tester = LLMAppTester(
    base_url="http://localhost:3000",
    visual_threshold=0.1,
    a11y_enabled=True
)

# 测试 LLM 聊天界面
tester.test_chat_interface(
    conversation=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ],
    assertions={
        "response_visible": True,
        "typing_indicator": False,
        "error_state": False
    }
)

# 测试 LLM 流式响应
tester.test_streaming_response(
    prompt="Tell me a story",
    assertions={
        "stream_started": True,
        "content_appearing": True,
        "stream_completed": True
    }
)
```

### 集成测试矩阵

| 测试类型 | 工具 | 说明 |
|---------|------|------|
| **视觉回归** | Playwright + Pillow | 截图对比，差异高亮 |
| **无障碍** | axe-core + Playwright | WCAG 2.1 AA 规则 |
| **UI 交互** | Playwright | 点击、填充、悬停、拖拽 |
| **网络请求** | Playwright | API 请求/响应监控 |
| **控制台错误** | Playwright | JS 错误捕获 |
| **性能** | Playwright | Core Web Vitals |

### 输出报告示例

```html
<!-- evalite-browser Report -->
<h1>Browser E2E Test Report</h1>
<div class="summary">
  <span class="passed">12 passed</span>
  <span class="failed">2 failed</span>
  <span class="visual-diff">3 visual differences</span>
  <span class="a11y-violations">5 a11y violations</span>
</div>

<div class="visual-diff">
  <h2>Visual Differences</h2>
  <img src="baseline/chat-page.png" />
  <img src="current/chat-page.png" />
  <img src="diffs/chat-page-diff.png" />
  <p>Diff: 8.3% pixel difference</p>
</div>

<div class="a11y-violations">
  <h2>A11y Violations</h2>
  <div class="violation critical">
    <p>color-contrast: 文本与背景对比度不足</p>
    <code>#chat-input</code>
  </div>
</div>
```

## 核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/browser_runner.py` | 主 CLI 入口 |
| `scripts/visual_comparator.py` | 视觉对比引擎 |
| `scripts/a11y_auditor.py` | 无障碍审计器 |
| `scripts/interaction_validator.py` | UI 交互验证 |
| `scripts/init.py` | 项目初始化 |

## 依赖项

```
playwright>=1.40.0
pillow>=10.0.0
click>=8.1.0
rich>=13.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

## 与天龙引擎集成

```yaml
#天龙九部协同
- 04验证师: browser_runner.py 作为 E2E 测试核心
- 05安全师: a11y_auditor.py 进行无障碍合规检测
- 06审查师: visual_comparator.py 进行视觉回归审查
- 07记录师: 生成完整测试报告归档
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始版本，基于 browser-qa 升级 |
