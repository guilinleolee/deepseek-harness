---
name: browser-testing
description: |
  基于浏览器开发者工具的端到端（E2E）测试：测试用例以Markdown记录，支持本地和部署验证。
  V8.1升级: 新增agent-browser语义定位器支持，AI原生测试能力+200%。
  触发词: E2E测试、浏览器测试、端到端测试、界面测试、语义测试、AI测试。
  使用场景: (1) 验证功能在本地和部署后是否按预期工作 (2) 记录测试过程和结果 (3) AI自动化测试。
author: github/cafe3310
adapted-by: Claude Code
version: 2.0.0
date: 2026-03-05
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - mcp__chrome-devtools__*
---

# 基于浏览器的端到端测试 V2.0

本技能定义了一套端到端（E2E）测试流程，通过浏览器工具进行手动或半自动化的界面测试。

**V8.1升级**: 新增 **agent-browser** 支持，提供AI原生的语义定位器和Accessibility Tree快照，测试稳定性提升200%。

## 触发条件

- 用户说"E2E测试"、"浏览器测试"、"端到端测试"
- 用户说"语义测试"、"AI测试"、"自动化测试"
- 需要为项目创建或执行测试
- 需要验证功能在本地和部署后是否都按预期工作
- 需要记录测试过程和结果以供回顾

## 测试引擎选择

### 方式1: agent-browser（推荐，AI原生）

**优势**: 语义定位器 + Accessibility Tree + 状态管理

```bash
# 打开页面
agent-browser open https://example.com

# 获取AI可读快照（核心）
agent-browser snapshot -i --json
# 输出: { "elements": [{ "ref": "@e1", "role": "button", "name": "提交" }] }

# 语义操作
agent-browser click @e1
agent-browser fill @e2 "test@example.com"

# 状态保存（断点续传）
agent-browser state save test-flow
agent-browser state load test-flow
```

### 方式2: Chrome DevTools MCP（传统）

**适用**: 已有Chrome浏览器实例

```
mcp__chrome-devtools__take_snapshot
mcp__chrome-devtools__click
mcp__chrome-devtools__fill
```

## 测试流程

### 步骤1: 本地测试优先

在本地环境中完成开发后：

1. 在本地运行应用
2. 使用agent-browser执行端到端测试
3. 记录测试结果

```bash
# 本地测试示例
agent-browser open http://localhost:3000
agent-browser snapshot -i --json
agent-browser click @e1
agent-browser get url
agent-browser screenshot tests/screenshot1.png
```

### 步骤2: 部署测试

本地测试全部通过后：

1. 将代码推送到 `main` 分支
2. 触发自动部署
3. 等待部署完成

### 步骤3: 验证部署

在部署后的页面上：

```bash
# 部署验证示例
agent-browser open https://your-app.vercel.app
agent-browser state load test-flow  # 复用本地测试状态
agent-browser snapshot -i --json
agent-browser screenshot tests/deployed-screenshot.png
```

## 语义定位器（V2.0核心）

### 元素引用

```bash
# 快照引用 (@e1, @e2...)
agent-browser snapshot -i --json
agent-browser click @e1

# ARIA role定位
agent-browser find role button click --name "提交"

# 文本定位
agent-browser find text "登录" click

# Label定位
agent-browser find label "用户名" fill "admin"
```

### AI友好输出

```bash
# JSON格式输出（供AI解析）
agent-browser snapshot -i --json

# 输出示例
{
  "elements": [
    { "ref": "@e1", "role": "textbox", "name": "用户名", "value": "" },
    { "ref": "@e2", "role": "textbox", "name": "密码", "value": "" },
    { "ref": "@e3", "role": "button", "name": "登录" }
  ]
}
```

## 测试用例规范

### 存放位置

每个应用的测试用例存放在 `tests/` 目录下。

### 文件结构

每个测试用例都是独立的 Markdown 文件：

```markdown
# 测试用例: [测试名称]

## 基本信息
- **创建时间**: YYYY-MM-DD-HH-mm
- **Commit Hash**: abc1234
- **Commit Message**: feat: 添加用户认证功能
- **测试引擎**: agent-browser v2.0

## 测试目的
[详细说明此测试用例要验证的功能或修复的问题]

## 环境信息
- **本地运行方式**: `npm run dev`
- **部署方式**: 自动部署到 Vercel

## 测试脚本
```bash
agent-browser open http://localhost:3000/login
agent-browser snapshot -i --json
agent-browser fill @e1 "test@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --url dashboard
agent-browser screenshot tests/login-success.png
```

## 预期结果
- URL变为 /dashboard
- 页面显示欢迎信息

## 实际结果
- **截图路径**: tests/YYYY-MM-DD-HH-mm-登录测试/screenshot1.png
- **验证状态**: ✅ 通过
- **快照引用**: @e1=用户名输入框, @e2=密码输入框, @e3=登录按钮
```

## 状态管理（断点续传）

```bash
# 保存测试状态
agent-browser state save login-tested

# 恢复测试状态（跳过已完成的步骤）
agent-browser state load login-tested

# 列出所有保存的状态
agent-browser state list

# 显示状态详情
agent-browser state show login-tested
```

## 云浏览器支持

```bash
# Browserbase（云端运行）
export BROWSERBASE_API_KEY=your_key
agent-browser open https://example.com -p browserbase

# Kernel（隐身模式）
export KERNEL_STEALTH=true
agent-browser open https://example.com -p kernel
```

## 天龙引擎集成

### 与04验证师协同

此技能为天龙引擎04验证师提供E2E测试能力：

| 能力 | V1.0 | V2.0 |
|------|------|------|
| 元素定位 | CSS选择器 | 语义定位器 |
| 页面理解 | HTML解析 | Accessibility Tree |
| 状态管理 | 无 | save/load |
| 云浏览器 | 无 | Browserbase/Kernel |
| 测试稳定性 | 基准 | +200% |

### 使用示例

```bash
# 触发技能
"为这个功能创建E2E测试用例"

# 执行语义测试
"使用agent-browser测试登录流程"

# AI自动化测试
"生成快照并自动执行测试"

# 查看测试结果
"显示最近的测试用例和结果"
```

## Chrome DevTools 工具（兼容）

本技能仍支持以下Chrome DevTools MCP工具：

- `mcp__chrome-devtools__take_snapshot` - 获取页面快照
- `mcp__chrome-devtools__take_screenshot` - 截取页面截图
- `mcp__chrome-devtools__click` - 点击元素
- `mcp__chrome-devtools__fill` - 填写表单
- `mcp__chrome-devtools__navigate_page` - 导航页面
- `mcp__chrome-devtools__list_console_messages` - 查看控制台消息
- `mcp__chrome-devtools__list_network_requests` - 查看网络请求

## 测试模板

```
tests/
├── YYYY-MM-DD-HH-mm-登录测试.md
│   └── YYYY-MM-DD-HH-mm-登录测试/
│       ├── screenshot1.png
│       ├── screenshot2.png
│       ├── states/
│       │   └── login-flow.json
│       └── test-log.txt
├── YYYY-MM-DD-HH-mm-注册测试.md
└── ...
```

## 相关技能

- `agent-browser-skill` - AI原生浏览器自动化
- `playwright-skill` - Playwright浏览器自动化
- `webapp-testing` - 本地Web应用测试
- `omnidebug-autopilot` - 自主调试技能