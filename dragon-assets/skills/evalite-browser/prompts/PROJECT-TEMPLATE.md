# 项目初始化提示词

## Evalite-Browser 项目创建模板

### 交互式初始化流程

```
欢迎使用 evalite-browser 项目初始化向导

? 请输入项目名称: (my-llm-app)
? 请输入项目目录: (./evalite-browser)
? 请选择浏览器: (1) chromium (2) firefox (3) webkit
? 是否安装浏览器: (Y/n)
? 是否创建示例测试: (Y/n)
? 是否初始化 Git: (Y/n)

正在创建项目结构...
✓ 创建目录结构完成
✓ 创建配置文件完成
✓ 创建示例测试完成
✓ 初始化 Git 完成

项目已创建! 继续阅读 README.md 开始使用。
```

### 默认项目结构

```
{project_name}/
├── evalite.config.yaml          # 配置文件
├── tests/                       # 测试用例目录
│   ├── visual/                 # 视觉测试
│   ├── a11y/                  # 无障碍测试
│   └── interaction/             # 交互测试
├── baseline/                    # 基线截图
├── current/                    # 当前截图
├── reports/                    # 测试报告
│   ├── diffs/                  # 差异截图
│   └── html/                   # HTML 报告
├── .gitignore
└── README.md
```

### 配置文件模板

```yaml
# evalite.config.yaml
project:
  name: {project_name}
  version: 1.0.0
  description: LLM 应用浏览器测试

browser:
  type: chromium
  headless: true
  viewport:
    width: 1280
    height: 720

visual:
  baseline_dir: ./baseline
  current_dir: ./current
  diff_dir: ./reports/diffs
  threshold: 0.1
  full_page: true
  animations_wait: 1000
  dynamic_content_wait: 500

a11y:
  standard: WCAG2AA
  rules: []
  include_iframes: true
  include_shadow_dom: true
  report_format: html

interaction:
  wait_timeout: 5000
  retry_attempts: 3
  retry_delay: 1000
  screenshot_on_error: true

reporting:
  formats:
    - html
    - json
    - markdown
  output_dir: ./reports
```

### 示例测试用例

#### 1. 基础页面测试

```json
{
  "name": "basic-page-test",
  "url": "http://localhost:3000/",
  "description": "验证首页基本功能",
  "steps": [
    {
      "action": "wait_for_selector",
      "selector": "body"
    },
    {
      "action": "screenshot",
      "name": "home-page"
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": "nav",
      "description": "导航栏可见"
    },
    {
      "type": "has_count",
      "selector": "nav a",
      "min": 3,
      "description": "至少 3 个导航链接"
    }
  ],
  "visual": {
    "enabled": true,
    "threshold": 0.1
  },
  "a11y": {
    "enabled": true,
    "rules": ["color-contrast", "label", "link-name"]
  }
}
```

#### 2. LLM 聊天交互测试

```json
{
  "name": "llm-chat-interaction",
  "url": "http://localhost:3000/chat",
  "description": "测试 LLM 聊天功能",
  "steps": [
    {
      "action": "wait_for_selector",
      "selector": "[data-testid='chat-input']",
      "timeout": 10000
    },
    {
      "action": "fill",
      "selector": "[data-testid='chat-input']",
      "value": "Hello!"
    },
    {
      "action": "click",
      "selector": "[data-testid='send-button']"
    },
    {
      "action": "wait_for_selector",
      "selector": "[data-testid='response']",
      "timeout": 30000
    },
    {
      "action": "screenshot",
      "name": "chat-response"
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": "[data-testid='chat-input']",
      "description": "输入框可见"
    },
    {
      "type": "visible",
      "selector": "[data-testid='send-button']",
      "description": "发送按钮可见"
    },
    {
      "type": "contains_text",
      "selector": "[data-testid='response']",
      "expected": "",
      "description": "响应包含文本"
    }
  ],
  "visual": {
    "enabled": true,
    "name": "chat-response-received"
  },
  "a11y": {
    "enabled": true,
    "rules": ["color-contrast", "label", "aria-required-attr"]
  }
}
```

#### 3. 表单验证测试

```json
{
  "name": "form-validation-test",
  "url": "http://localhost:3000/form",
  "description": "测试表单验证功能",
  "steps": [
    {
      "action": "click",
      "selector": "[type='submit']"
    },
    {
      "action": "wait_for_selector",
      "selector": ".error-message",
      "timeout": 5000
    }
  ],
  "assertions": [
    {
      "type": "contains_text",
      "selector": ".error-message",
      "expected": "required",
      "description": "显示必填错误"
    },
    {
      "type": "disabled",
      "selector": "[type='submit']",
      "description": "提交按钮禁用直到表单有效"
    }
  ]
}
```

### 初始化命令

```bash
# 创建新项目
evalite init my-llm-app --template basic

# 使用指定模板
evalite init my-app --template chat

# 列出可用模板
evalite templates list

# 运行测试
evalite run --config tests/basic-test.json

# 运行所有测试
evalite run --all

# 生成报告
evalite report --format html,json

# 基线管理
evalite baseline update           # 更新所有基线
evalite baseline update --test basic-test  # 更新指定测试
evalite baseline approve --test basic-test # 审批变更
```

### 环境变量配置

```bash
# .env 文件
EVALITE_URL=http://localhost:3000
EVALITE_BROWSER=chromium
EVALITE_HEADLESS=true
EVALITE_VIEWPORT_WIDTH=1280
EVALITE_VIEWPORT_HEIGHT=720

# API 密钥 (如需要)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```
